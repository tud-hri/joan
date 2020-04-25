import os

from PyQt5 import QtCore, QtWidgets

from process import Control, State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from modules.joanmodules import JOANModules
from modules.experimentmanager.action.states import ExperimentManagerStates
from modules.experimentmanager.action.experimentmanageraction import ExperimentManagerAction


class ExperimentManagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, module_action=module_action, master_state_handler=master_state_handler, parent=parent)

        self.module_widget.btn_initialize_condition.clicked.connect(
            lambda idx: self.module_action.initialize_condition(self.module_widget.combobox_conditions.currentIndex())
        )

        self._file_menu = self.menu_bar.addMenu('File')
        self._file_menu.addAction('Load experiment', self.process_menu_load_experiment)

    def process_menu_load_experiment(self):
        '''Process menu command to load an experiment file'''
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("Settings files (*.xml *.json)")
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if dialog.exec():
            self.module_action.load_experiment(dialog.selectedFiles())
