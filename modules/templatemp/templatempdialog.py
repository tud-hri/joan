from core.moduledialog import ModuleDialog
from core.modulemanager import ModuleManager
from modules.joanmodules import JOANModules


class TemplateMPDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.TEMPLATE_MP, module_manager=module_manager, parent=parent)
