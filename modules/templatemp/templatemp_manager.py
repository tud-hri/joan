from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class TemplateMPManager(ModuleManager):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.TEMPLATE_MP, time_step_in_ms=time_step_in_ms, parent=parent)

