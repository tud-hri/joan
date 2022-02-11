from core.module_process import ModuleProcess
from modules.dataplotter.dataplotter_settings import DataPlotterSettings
from modules.joanmodules import JOANModules


class DataPlotterProcess(ModuleProcess):
    """
    For the Dataplotter this is a bit of a redundant class becasue everything happens within the dialog. But we
    still need it for JOAN to run, and to link our variables to be plotted to the settings in get ready.
    """
    settings: DataPlotterSettings

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton, pipe_comm):
        """

        :param module: DataPlotter
        :param time_step_in_ms:
        :param news:
        :param settings:
        :param events:
        :param settings_singleton:
        """
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events,
                         settings_singleton=settings_singleton, pipe_comm=pipe_comm)
        self.settings = settings
        self.news = news

        self.variables_to_be_plotted = {}
        self.save_path = ''

        self.file = None

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings are converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        self.variables_to_be_plotted = self.settings.variables_to_be_plotted
