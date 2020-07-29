from PyQt5 import QtWidgets

import os
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog

from .newexperimentdialog import NewExperimentDialog


class ExperimentManagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, module_action=module_action, use_state_machine_and_timer=False, parent=parent)

        self.module_widget.initializeExperimentPushButton.clicked.connect(self.initialize_new_experiment)
        self.module_widget.saveExperimentPushButton.clicked.connect(self.save_experiment)
        self.module_widget.loadExperimentPushButton.clicked.connect(self.load_experiment)

    def initialize_new_experiment(self):
        new_experiment_dialog = NewExperimentDialog(self.module_action.singleton_settings.all_settings_keys, parent=self)
        new_experiment_dialog.accepted.connect(
            lambda: self.module_action.initialize_new_experiment(new_experiment_dialog.modules_to_include, new_experiment_dialog.file_path))

    def load_experiment(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Experiment', filter='JSON (*.json)')
        if file_path:
            self.module_action.load_experiment(file_path)

    def save_experiment(self):
        self.module_action.save_experiment()

    def update_gui(self):
        self.module_widget.experimentNameLabel.setText(os.path.abspath(self.module_action.experiment_save_path).split('\\')[-1])
