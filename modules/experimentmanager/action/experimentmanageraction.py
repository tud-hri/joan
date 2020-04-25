from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import ExperimentManagerStates


class ExperimentManagerAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=100):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(ExperimentManagerStates.EXPERIMENTMANAGER.READY)

        self.data = {}
        self.write_news(news=self.data)   

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        # self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        pass

    def start(self):
        try:
            self.module_state_handler.request_state_change(ExperimentManagerStates.EXPERIMENTMANAGER.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(ExperimentManagerStates.EXPERIMENTMANAGER.STOPPED)
        except RuntimeError:
            return False
        return super().stop()

    def initialize_condition(self, condition_nr):
        '''Initialize JOAN for the chosen condition'''
        print('settings for condition '+str(condition_nr))

    def load_experiment(self, experiment_settings_file):
        '''All the action stuff for loading a new experiment settings file'''
        print('loading experiment_settings_file: '+str(experiment_settings_file))
