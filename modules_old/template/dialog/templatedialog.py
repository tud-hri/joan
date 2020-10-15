from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from core.joanmoduleaction import JoanModuleAction
from core.joanmoduledialog import JoanModuleDialog


class TemplateDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.TEMPLATE, module_action=module_action, parent=parent)

        self.parent = parent

        # The modules work with states. Also see: TemplateAction in templateaction.py
        # Each JOAN module has its own state machine that can be customized by adding module specific transition conditions
        # Besides that the state machine supports entry actions and and exit actions per state. For more info on the state machine check core/statemachine.py
        # for more info on the possible states check core/statesenum.py
        # the state machine is part of the module_action which is passed through as an argument in the module_dialog

        # a list of methods can be added to the state_machine listener
        # a state change listener is implemented as a callable method which is executed when state_machine.request_state_change is used
        self.module_action.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_dialog_1)
        self.module_action.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_dialog_2)

    def _execute_on_state_change_in_module_dialog_1(self):
        # example of adding a method to be executed on a state change request
        pass

    def _execute_on_state_change_in_module_dialog_2(self):
        # example of adding a method to be executed on a state change request
        pass
