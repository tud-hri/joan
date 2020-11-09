import enum

from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class ControllerPlotterSettings(ModuleSettings):
    """
    This class is not used however we should still define it according to the joan structure
    """
    def __init__(self):
        super().__init__(JOANModules.CONTROLLER_PLOTTER)