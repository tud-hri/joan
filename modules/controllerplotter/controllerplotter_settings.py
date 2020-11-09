import enum

from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class ControllerPlotterSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.CONTROLLER_PLOTTER)