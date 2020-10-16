from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news)


    def do_function(self):
        self._sharedvalues_module.hardware_variable += 1.0
        pass

