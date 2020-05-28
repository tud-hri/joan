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
from .templatesettings import TemplateSettings
from process.settings import ModuleSettings


class TemplateAction(JoanModuleAction):
    """Example JOAN module"""

    def __init__(self, master_state_handler, millis=100):
        super().__init__(module=JOANModules.TEMPLATE, master_state_handler=master_state_handler, millis=millis)

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
        # To create settings for your costum module create a settings class and enherit JOANMOduleSetting, as in the example TempleSettings
        # All attributes you add to your settings class will automatically be save if you call setting.save_to_file
        # when loading setting, all attribute in the JSON file are copied, but missing values will keep their default value as defined in your setting class

        # first create a settings object containing the default values
        self.settings = TemplateSettings(module_enum=JOANModules.TEMPLATE)

        # then load the saved value from a file, this can be done here, or implement a button with which the user can specify the file to load from.
        default_settings_file_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template_settings.json')
        if os.path.isfile(default_settings_file_location):
            self.settings.load_from_file(default_settings_file_location)

        # now you can copy the current settings as attributes of the action class, but please note that it is also possible to access the settings directly.
        self.millis = self.settings.millis

        # finale update the new setting to the settings singleton (such that other modules can also see this module's settings)
        self.share_settings(self.settings)
        # end settings for this module

    def load_settings_from_file(self, settings_file_to_load):
        self.settings.load_from_file(settings_file_to_load)
        self.share_settings(self.settings)

    def save_settings_to_file(self, file_to_save_in):
        self.settings.save_to_file(file_to_save_in)

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
        # This is de place to do all initialization needed. In the example here, the necessary settings are copied from the settings object.
        # This is done during the initialization to prevent settings from changing while the module is running. This does mean that the module needs to be
        # reinitialised every time the settings are changed.
        self.millis = self.settings.millis

        try:
            self.module_state_handler.request_state_change(TemplateStates.INITIALIZED)
        except RuntimeError:
            return False
        return True

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
