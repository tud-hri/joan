from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class TemplateMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, start_event=, exception_event=exception_event)

    def do_while_running(self):
        pass

