
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
from .states import TemplateStates
from process.settings import ModuleSettings

class TemplateAction(JoanModuleAction):
    """Example JOAN module"""
    def __init__(self, millis=100):
        super().__init__(module=JOANModules.TEMPLATE, millis=millis)
    #def __init__(self, master_state_handler, millis=100):
    #    super().__init__(module=JOANModules.TEMPLATE, master_state_handler=master_state_handler, millis=millis)

        # The modules work with states.
        # Each JOAN module has its own module states (e.g. states specific for the module, see states.py in the template action folder) 
        # and master states, which control the entire program.
        # Checkout other modules for examples how to implement these states
        self.module_state_handler.request_state_change(TemplateStates.EXEC.READY)

        # start news for the datarecorder.
        # here, we are added a variable called 'datawriter output' to this modules News. 
        # You can choose your own variable names and you can add as many vairables to self.data as you want.
        self.data['datawriter output'] = 2020
        self.write_news(news=self.data)
        self.time = QtCore.QTime()
        # end news for the datarecorder

        # start settings for this module
        # each module has its own settings, which are stored in a .json file (e.g. template_settings.json)
        self.settings_object = ModuleSettings(file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template_settings.json'))
        self.settings = self.settings_object.read_settings()
        
        try:
            self.millis = self.settings['data'][JOANModules.TEMPLATE.name]['millis_pulse']
        except KeyError:
            self.millis = 100

        # you can customize the settings of your module. Below we add a couple of examples.
        # you could also add these manually to the json file directly, but make sure that you properly 
        # read the settings from the json and set the variable here in self.update_settings
        self.my_settings_dict = {}
        self.some_settings = 'value'
        self.steer_sensitivity = 50
        self.throttle_sensitivity = 50
        self.brake_sensitivity = 50
        self.my_settings_dict['millis_pulse'] = self.millis
        self.my_settings_dict['some_settings'] = self.some_settings
        self.my_settings_dict['steer_sensitivity'] = self.steer_sensitivity
        self.my_settings_dict['throttle_sensitivity'] = self.throttle_sensitivity
        self.my_settings_dict['brake_sensitivity'] = self.brake_sensitivity

        # and we write these settings to the json file
        self.settings_object.write_settings(group_key=JOANModules.TEMPLATE.name, item=self.my_settings_dict)
        # and update the new setting to the settings singleton (such that other modules can also see this module's settings)
        self.update_settings(self.settings)
        # end settings for this module

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """

        # in this template example, we update the 'datawriter output' news with the elapsed time.
        self.data['datawriter output'] = self.time.elapsed()

        # and we write the news (actually update the news), such that all the other modules get the latest value of 'datawriter output'
        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        try:
            self.module_state_handler.request_state_change(TemplateStates.INIT.INITIALIZING)
        except RuntimeError:
            return False

        # start settings from singleton
        try:
            singleton_settings = self.singleton_settings.get_settings(JOANModules.TEMPLATE)
            settings_dict = singleton_settings['data'][JOANModules.TEMPLATE.name]
            self.millis = settings_dict['millis_pulse']
            self.some_settings = settings_dict['some_settings']
            self.steer_sensitivity = settings_dict['steer_sensitivity']
            self.throttle_sensitivity = settings_dict['throttle_sensitivity']
            self.brake_sensitivity = settings_dict['brake_sensitivity']
        except KeyError as inst:
            print('KeyError:', inst)
            return False
        return True
        # end settings from singleton

    def start(self):
        """start the module"""
        try:
            # here you perform any operation that is needed to start the module. 
            # In our case, we start the timer.
            self.module_state_handler.request_state_change(TemplateStates.EXEC.RUNNING)
            self.time.restart()
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        """stop the module"""
        try:
            # do anything that is needed when the module is stopped
            self.module_state_handler.request_state_change(TemplateStates.EXEC.STOPPED)
        except RuntimeError:
            return False
        return super().stop()
