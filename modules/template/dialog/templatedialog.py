from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog


class TemplateDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.TEMPLATE, module_action=module_action, parent=parent)

        self.parent = parent

        # The modules work with states. Also see: TemplateAction in templateaction.py
        # Each JOAN module has its own state machine that can be customized by adding module specific transition conditions
        # Besides that the state machine supports entry actions and and exit actions per state. For more info on the state machine check process/statemachine.py
        # for more info on the possible states check process/statesenum.py
        # the state machine is part of the module_action which is passed through as an argument in the module_dialog

        # a list of methods can be added to the state_machine listener
        # a state change listener is implemented as a callable method which is executed when state_machine.request_state_change is used
        self.module_action.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_dialog_1)
        self.module_action.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_dialog_2)

        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)

    def _load_settings(self):
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings', filter='*.json')
        if settings_file_to_load:
            self.module_action.load_settings_from_file(settings_file_to_load)

    def _save_settings(self):
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings', filter='*.json')
        if file_to_save_in:
            self.module_action.save_settings_to_file(file_to_save_in)

    def _execute_on_state_change_in_module_dialog_1(self):
        # example of adding a method to be executed on a state change request
        pass

    def _execute_on_state_change_in_module_dialog_2(self):
        # example of adding a method to be executed on a state change request
        pass
