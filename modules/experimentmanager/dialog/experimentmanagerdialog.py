import os

from PyQt5 import QtCore

from process import Control, State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from modules.joanmodules import JOANModules
from modules.experimentmanager.action.states import ExperimentManagerStates
from modules.experimentmanager.action.experimentmanageraction import ExperimentManagerAction


class ExperimentManagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, module_action=module_action, master_state_handler=master_state_handler, parent=parent)

        self.module_widget.btn_initialize_condition.clicked.connect(self.initialize_condition)

    def initialize_condition(self):
        '''Initialize JOAN for the chosen condition'''
        condition_nr = self.module_widget.combobox_conditions.currentIndex()

        if condition_nr is not -1:
            print('settings for condition')
