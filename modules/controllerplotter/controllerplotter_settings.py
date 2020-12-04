import enum

from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class ControllerPlotterSettings(ModuleSettings):
    """
    Every module should have a settings object, even if it's unused to conform to the standard JOAN module structure
    """
    def __init__(self):
        super().__init__(JOANModules.CONTROLLER_PLOTTER)
