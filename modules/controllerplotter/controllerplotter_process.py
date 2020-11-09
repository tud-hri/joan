from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from datetime import datetime


class ControllerPlotterProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton= settings_singleton)


    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings ar converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        pass

    def do_while_running(self):
        """
        do_while_running something and write the result in a shared_variable
        """
        pass