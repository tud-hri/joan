from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class TemplateDialog(ModuleDialog):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    Inherits from ModuleDialog so every module has a common dialog window
    The result is that the look and feel is the same for every module while maintaining module-specific dialogs
    """
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.TEMPLATE, module_manager=module_manager, parent=parent)

    def update_dialog(self):
        """
        Update the dialog based on a variable in the shared values
        :return:
        """
        if self.module_manager.shared_variables:
            self.module_widget.lbl_time.setText("State: " + str(self.module_manager.shared_variables.state))
