import os

from PyQt5 import QtCore, QtWidgets

from process import State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from modules.joanmodules import JOANModules
from modules.experimentmanager.action.states import ExperimentManagerStates
from modules.experimentmanager.action.experimentmanageraction import ExperimentManagerAction


class ExperimentManagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, module_action=module_action, parent=parent)
    #def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
    #    super().__init__(module=JOANModules.EXPERIMENT_MANAGER, module_action=module_action, master_state_handler=master_state_handler, parent=parent)

        self.module_widget.btn_initialize_condition.clicked.connect(
            lambda idx: self.module_action.initialize_condition(self.module_widget.combobox_conditions.currentIndex())
        )
        self.module_widget.btn_initialize_condition.clicked.connect(
            lambda idx: self.initialize_condition()
        )

        self.file_menu.addAction('Load experiment', self.process_menu_load_experiment)

    def process_menu_load_experiment(self):
        '''Process menu command to load an experiment file'''
        dialog = QtWidgets.QFileDialog(self)
        dialog.setNameFilter("Settings files (*.json)")
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        dialog.setDirectory(os.path.abspath(os.getcwd()))

        if dialog.exec():
            result = self.module_action.load_experiment(dialog.selectedFiles())
            if not isinstance(result, dict):
                self.module_widget.lbl_message_loadjson.setText(result)   # catch json errors and show them on screen
            else:
                self.module_widget.lbl_message_loadjson.setText('JSON is valid!')
                self.process_experiment_conditions()

    def process_experiment_conditions(self):
        """process the experiment conditions"""
        self.module_widget.combobox_conditions.clear()
        self.module_widget.combobox_conditions.addItems(self.module_action.get_experiment_conditions())

    def initialize_condition(self):
        """
        This function is called before the module is started
        """
        try:
            self.module_action.module_state_handler.request_state_change(ExperimentManagerStates.INIT.INITIALIZED)
        except RuntimeError:
            return False

    def handle_module_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.module_action.module_state_handler.get_state(state)  # ensure we have the State object (not the int)
            # update the state label
            self.state_widget.lbl_module_state.setText(state_as_state.name)
            self.module_widget.repaint()

        except Exception as inst:
            print(inst)

