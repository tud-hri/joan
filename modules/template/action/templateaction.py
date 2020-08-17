"""
TemplateAction class

This is a template for creating new JOAN modules
We tried to explain how a module works through the comments and 
will keep adding explanation as new functionality is added to the module

"""
import os

from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State
from .templatesettings import TemplateSettings
from .templatesignals import TemplateSignals


class TemplateAction(JoanModuleAction):
    """Example JOAN module"""

    def __init__(self, millis=100):
        super().__init__(module=JOANModules.TEMPLATE, millis=millis)

        # The modules work with states. Also see: TemplateDialog in templatedialog.py
        # Each JOAN module has its own state machine that can be customized by adding module specific transition conditions
        # Besides that the state machine supports entry actions and and exit actions per state. For more info on the state machine check process/statemachine.py
        # for more info on the possible states check process/statesenum.py
        #
        # transition conditions are called when transitioning and can impose simple or more complex rules to check is a state transition is legal.
        # If a state change is illegal it is also possible to add an error message explaining why the state change is illegal
        # what follows are an example of a simple en more complex condition:
        self.state_machine.set_transition_condition(State.IDLE, State.READY, lambda: self.millis > 10)
        self.state_machine.set_transition_condition(State.READY, State.RUNNING, self._starting_condition)

        # another possibility is to add entry and exit actions for states. This actions are executed when a state is entered or exited for example
        self.state_machine.set_entry_action(State.RUNNING, lambda: print('Template is starting.'))
        self.state_machine.set_exit_action(State.RUNNING, self._clean_up_after_run)

        # a list of methods can be added to the state_machine listener
        # a state change listener is implemented as a callable method which is executed when state_machine.request_state_change is used
        self.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_action_1)
        self.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_action_2)

        # Finally it is also possible to define automatic state changes. If state A is entered and the transition to state B is immediately legal, the state
        # machine will automatically progress to state B. It is possible to define one automatic state change per state, except for the Error state. It is
        # illegal to automatically leave the Error state for safety reasons. Not that state A wil not be skipped, but exited automatically. So the state changes
        # are subject to all normal conditions and entry and exit actions. 
        # Note: This means that a transition condition must be defined!
        self.state_machine.set_automatic_transition(State.READY, State.RUNNING)

        # start news for the datarecorder.
        # here, we are added a variable called 'datawriter output' to this modules News. 
        # You can choose your own variable names and you can add as many vairables to self.data as you want.
        self.data['datawriter output'] = 2020
        self.data['nesting'] = {'example 1': 44, 'example 2': 35}
        self.counter = 0  # see def do(self):
        self.sign = 1     # see def do(self):
        self.write_news(news=self.data)
        self.time = QtCore.QTime()
        # end news for the datarecorder

        # start settings for this module
        # each module has its own settings, which are stored in a .json file (e.g. template_settings.json)
        # To create settings for your custom module create a settings class and enherit JOANMOduleSetting, as in the example TempleSettings
        # All attributes you add to your settings class will automatically be save if you call setting.save_to_file
        # when loading setting, all attribute in the JSON file are copied, but missing values will keep their default value as defined in your setting class

        # first create a settings object containing the default values
        self.settings = TemplateSettings(module_enum=JOANModules.TEMPLATE)

        # then load the saved value from a file, this can be done here, or implement a button with which the user can specify the file to load from.
        default_settings_file_location = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                      'template_settings.json')
        if os.path.isfile(default_settings_file_location):
            self.settings.load_from_file(default_settings_file_location)

        # now you can copy the current settings as attributes of the action class, but please note that it is also possible to access the settings directly.
        self.millis = self.settings.millis

        # finale update the new setting to the settings singleton (such that other modules can also see this module's settings)
        self.share_settings(self.settings)
        # end settings for this module

        # template signals
        # in templatesignals.py the pyqtsignals are defined to trigger specific actions from this module
        # here, connect the function to the appropriate signal
        self._module_signals = TemplateSignals(self.module)
        self.singleton_signals.add_signals(self.module, self._module_signals)

        # we connect a dummy
        self._module_signals.my_custom_signal_str.connect(self.test_slot)

        # here's a way how to emit one of the module_signals. This can be done in any module
        self.singleton_signals.get_signals(self.module).my_custom_signal_str.emit("TEMPLATE: signal test")

    def test_slot(self, message):
        """
        Dummy function to illustrate the signal-slot functionality
        :param message:
        :return: prints stuffs
        """
        print(message)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """

        # in this template example, we update the 'datawriter output' news with the elapsed time.
        self.data['datawriter output'] = self.time.elapsed()

        # and we write the news (actually update the news), such that all the other modules get the latest value of 'datawriter output'
        if self.counter < 1:
            self.sign = -1
        if self.counter > 99:
            self.sign = 1
        self.data['counter'] = self.counter * self.sign
        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        # This is de place to do all initialization needed. In the example here, the necessary settings are copied from the settings object.
        # This is done during the initialization to prevent settings from changing while the module is running. This does mean that the module needs to be
        # reinitialised every time the settings are changed.
        self.data['counter'] = self.counter
        self.write_news(news=self.data)
        
        self.millis = self.settings.millis

        # if (self.state_machine.current_state is State.IDLE):
        self.state_machine.request_state_change(State.READY)  # , "You can now start the module")
        # elif (self.state_machine.current_state is State.ERROR):
        #    self.state_machine.request_state_change(State.IDLE)
        return super().initialize()

    def start(self):
        """start the module"""
        self.state_machine.request_state_change(target_state=State.RUNNING)
        return super().start()

    def stop(self):
        """stop the module"""
        # Will automatically go to READY as defined above in self.state_machine.set_automatic_transition
        self.state_machine.request_state_change(State.IDLE)

        return super().stop()

    def _starting_condition(self):
        """
        This is an example of a transition condition for the state machine. If this condition is true, the transition to the running state is allowed. Also
        check the setting of this condition in the constructor of this class.

        :return: (bool) legality of state change, (str) error message
        """
        try:
            if self.singleton_status.get_module_current_state(JOANModules.HARDWARE_MANAGER) is State.RUNNING:
                return True, ''
            return False, 'The hardware manager should be running before starting the Template module.'
        except KeyError:
            return False, 'The hardware manager state could not be read, but it should be running before starting template.'

    def _clean_up_after_run(self):
        """
        This is an example of an exit action for a state, if the running state is exited, this function is executed. This can be used to clean up connections,
        close files or do other final actions. Also check the setting of this action in the constructor of this class. Please note that this action is always
        called, no matter the target state after the state change. It can be compared with the finally statement in exeption handling.
        :return: None
        """
        # do some interesting multi line cleaning up of the mess I made during execution.
        pass

    def _execute_on_state_change_in_module_action_1(self):
        # example of adding a method to be executed on a state change request
        pass

    def _execute_on_state_change_in_module_action_2(self):
        # example of adding a method to be executed on a state change request
        pass
