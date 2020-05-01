from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import TemplateStates

# Used for Settings
import os
from process.settings import ModuleSettings


class TemplateAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=100):
        super().__init__(module=JOANModules.TEMPLATE, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(TemplateStates.TEMPLATE.READY)

        # start news for the datarecorder
        self.data['datawriter output'] = 2020
        self.write_news(news=self.data)
        self.time = QtCore.QTime()
        # end news for the datarecorder

        # start settings for this module
        self.settings_object = ModuleSettings(file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template_settings.json'))
        self.settings = self.settings_object.read_settings()
        self.item_dict = {}
        try:
            self.millis = self.settings['data'][JOANModules.TEMPLATE.name]['millis_pulse']
        except KeyError:
            self.millis = 100

        self.some_settings = 'value'
        self.steer_sensitivity = 50
        self.throttle_sensitivity = 50
        self.brake_sensitivity = 50
        self.item_dict['millis_pulse'] = self.millis
        self.item_dict['some_settings'] = self.some_settings
        self.item_dict['steer_sensitivity'] = self.steer_sensitivity
        self.item_dict['throttle_sensitivity'] = self.throttle_sensitivity
        self.item_dict['brake_sensitivity'] = self.brake_sensitivity

        self.settings_object.write_settings(group_key=JOANModules.TEMPLATE.name, item=self.item_dict)

        self.update_settings(self.settings)
        # end settings for this module

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        self.data['datawriter output'] = self.time.elapsed()
        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        print("initialized")
        # start settings from singleton
        try:
            singleton_settings = self.singleton_settings.get_settings(JOANModules.TEMPLATE)
            item_dict = singleton_settings['data'][JOANModules.TEMPLATE.name]
            self.millis = item_dict['millis_pulse']
            self.some_settings = item_dict['some_settings']
            self.steer_sensitivity = item_dict['steer_sensitivity']
            self.throttle_sensitivity = item_dict['throttle_sensitivity']
            self.brake_sensitivity = item_dict['brake_sensitivity']
        except KeyError as inst:
            print('KeyError:', inst)
            return False
        return True
        # end settings from singleton

    def start(self):
        try:
            self.module_state_handler.request_state_change(TemplateStates.TEMPLATE.RUNNING)
            self.time.restart()
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(TemplateStates.TEMPLATE.STOPPED)
        except RuntimeError:
            return False
        return super().stop()
