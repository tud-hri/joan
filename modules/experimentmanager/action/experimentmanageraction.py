import os

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.settings import ModuleSettings
from .experiment import Experiment


class ExperimentManagerAction(JoanModuleAction):
    def __init__(self, millis=100):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, use_state_machine_and_timer=False)

        # create/get default experiment_settings
        self.my_file = os.path.join('.', 'default_experiment_settings.json')
        # First remove current file
        if os.path.exists(self.my_file):
            os.remove(self.my_file)

        self.current_experiment = None
        self.experiment_save_path = ''

    def initialize_new_experiment(self, modules_to_include, save_path):
        self.current_experiment = Experiment(modules_to_include)
        self.current_experiment.set_from_current_settings(self.singleton_settings)
        self.experiment_save_path = save_path
        self.save_experiment()

        self.module_dialog.update_gui()

    def save_experiment(self):
        if self.current_experiment:
            self.current_experiment.save_to_file(self.experiment_save_path)
            self.module_dialog.update_gui()

    def load_experiment(self, file_path):
        self.current_experiment = Experiment.load_from_file(file_path)
        self.module_dialog.update_gui()
