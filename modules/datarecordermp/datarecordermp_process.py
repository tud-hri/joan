from core.module_process import ModuleProcess
# rom modules.datarecordermp.writermp.newswritermp import DataWriter
from modules.datarecordermp.datarecordermp_settings import DatarecorderMPSettings
from modules.joanmodules import JOANModules


class DatarecorderMPProcess(ModuleProcess):
    settings: DatarecorderMPSettings

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)
        self.settings = settings
        self.news = news

        self.variables_to_be_saved = {}
        self.save_path = ''

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings are converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        self.variables_to_be_saved = self.settings.variables_to_be_saved
        self.save_path = self.settings.path_to_save_file

    def do_while_running(self):
        """
        do_while_running something and, dfor datarecorder, read the result from a shared_variable
        """
        # TODO implement writing to file
        pass
