from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class CarlaInterfaceDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.CARLA_INTERFACE, module_manager=module_manager, parent=parent)

    def update_dialog(self):
        """
        Update the dialog based on a variable in the shared values
        :return:
        """
        if self.module_manager.shared_variables:
            self._module_widget.lbl_time.setText("State: " + str(self.module_manager.shared_variables.state))
