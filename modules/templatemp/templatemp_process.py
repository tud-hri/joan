from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class TemplateMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, start_event, exception_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, start_event=start_event, exception_event=exception_event)

        self.shared_values_hardware = news.read_news(JOANModules.HARDWARE_MP)

    def do(self):
        pass
