from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class TemplateMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step, news):
        super().__init__(module, time_step=time_step, news=news)

    def do_function(self):
        pass

