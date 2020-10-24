from core.module_process import ModuleProcess
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event, exception_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, start_event=start_event, exception_event=exception_event)
        self.input_objects = {}

    def get_ready(self):
        # Create empty settings object in which we will reconstruct our settings dictionary
        super().get_ready()

        # TODO, change using sharedvalues_module to settings
        # Create the object that are in the settings here
        for idx, keyboards in enumerate(self._module_shared_variables.keyboards):
            self.input_objects[keyboards] = HardwareInputTypes.KEYBOARD.klass_mp(settings=self._settings_as_object.keyboards[idx],
                                                                                 shared_variables=self._module_shared_variables.keyboards[keyboards])

        for idx, joysticks in enumerate(self._module_shared_variables.joysticks):
            self.input_objects[joysticks] = HardwareInputTypes.JOYSTICK.klass_mp(settings=self._settings_as_object.joysticks[idx],
                                                                                 shared_variables=self._module_shared_variables.joysticks[joysticks])

        for idx, sensodrives in enumerate(self._module_shared_variables.sensodrives):
            self.input_objects[sensodrives] = HardwareInputTypes.SENSODRIVE.klass_mp(settings=self._settings_as_object.sensodrives[idx],
                                                                                     shared_variables=self._module_shared_variables.sensodrives[sensodrives])

    def do_while_running(self):
        for inputs in self.input_objects:
            # will perform the mp input class for eaach available input
            self.input_objects[inputs].do()
