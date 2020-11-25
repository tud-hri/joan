from core.module_process import ModuleProcess
from modules.dataplotter.dataplotter_settings import DataPlotterSettings
from modules.joanmodules import JOANModules


class DataPlotterProcess(ModuleProcess):
    settings: DataPlotterSettings

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)
        self.settings = settings
        self.news = news

        self.variables_to_be_saved = {}
        self.save_path = ''

        self.file = None

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings are converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        self.variables_to_be_plotted = self.settings.variables_to_be_plotted


    def _run_loop(self):
        pass

    def do_while_running(self):
        """
        do_while_running something and, for dataplotter, read the result from a shared_variable
        """
        pass

