from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step, news):
        super().__init__(module, time_step=time_step, news=news)


    def do_function(self):
        self._sharedvalues_module.hardware_variable += 1.0
        pass

