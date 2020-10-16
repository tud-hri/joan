from modules.joanmodules import JOANModules
from core.joanmoduleaction import JoanModuleAction
from core.joanmoduledialog import JoanModuleDialog


class ControllerPlotterDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.CONTROLLER_PLOTTER, module_action=module_action, parent=parent)

        self.parent = parent

        self.module_action.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_dialog_1)
        self.module_action.state_machine.add_state_change_listener(self._execute_on_state_change_in_module_dialog_2)

    def _execute_on_state_change_in_module_dialog_1(self):
        # example of adding a method to be executed on a state change request
        pass

    def _execute_on_state_change_in_module_dialog_2(self):
        # example of adding a method to be executed on a state change request
        pass
