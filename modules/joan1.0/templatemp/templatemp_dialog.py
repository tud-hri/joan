from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class TemplateMPDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.TEMPLATE_MP, module_manager=module_manager, parent=parent)

    def update_dialog(self):
        if self._module_manager.shared_variables:
            self._module_widget.lbl_time.setText("Time: " + str(self._module_manager.shared_variables.time))