from core.module_process import ModuleProcess
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules
import time

class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event, exception_event, process_is_ready_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings,
                         start_event=start_event, exception_event=exception_event, process_is_ready_event=process_is_ready_event)
        self.input_classes = {}

    def get_ready(self):
        super().get_ready()

        # Create appropriate classes here (note that when a sensodrive is created it will start its own process, whereas the keyboards and joysticks do_while_running not)
        for idx, keyboards in enumerate(self._module_shared_variables.keyboards):
            self.input_classes[keyboards] = HardwareInputTypes.KEYBOARD.klass_mp(settings=self._settings_as_object.keyboards[idx],
                                                                                 shared_variables=self._module_shared_variables.keyboards[keyboards])

        for idx, joysticks in enumerate(self._module_shared_variables.joysticks):
            self.input_classes[joysticks] = HardwareInputTypes.JOYSTICK.klass_mp(settings=self._settings_as_object.joysticks[idx],
                                                                                 shared_variables=self._module_shared_variables.joysticks[joysticks])

    def do_while_running(self):
        for inputs in self.input_classes:
            # will perform the mp input class for each available input
            self.input_classes[inputs].do_while_running()
