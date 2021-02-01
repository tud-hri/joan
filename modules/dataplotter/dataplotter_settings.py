from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class DataPlotterSettings(ModuleSettings):
    """
    For the DataPlotter this is an empty class since it does not need any Settings.
    """
    def __init__(self):
        super().__init__(module=JOANModules.DATA_PLOTTER)

        self.variables_to_be_plotted = []
