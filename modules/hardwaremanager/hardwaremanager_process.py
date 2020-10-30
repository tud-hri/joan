from core.module_process import ModuleProcess
from modules.hardwaremanager.hardwaremanager_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules


class HardwareManagerProcess(ModuleProcess):
    """
    Overall process that inherits from ModuleProcess (will loop at the desired frequency)
    """
    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events)
        self.input_objects = {}

    def get_ready(self):
        # Create the objects that are in the settings here
        for key, value in self._settings_as_object.keyboards.items():
            self.input_objects[key] = HardwareInputTypes.KEYBOARD.process(settings=value, shared_variables=self._module_shared_variables.keyboards[key])

        for key, value in self._settings_as_object.joysticks.items():
            self.input_objects[key] = HardwareInputTypes.JOYSTICK.process(settings=value, shared_variables=self._module_shared_variables.joysticks[key])

        for key, value in self._settings_as_object.sensodrives.items():
            self.input_objects[key] = HardwareInputTypes.SENSODRIVE.process(settings=value, shared_variables=self._module_shared_variables.sensodrives[key])

    def do_while_running(self):
        for inputs in self.input_objects:
            # will perform the mp input class for eaach available input
            self.input_objects[inputs].do()

