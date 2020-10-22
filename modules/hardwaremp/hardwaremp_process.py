from core.module_process import ModuleProcess
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules
from modules.hardwaremp.hardwaremp_settings import HardwareMPSettings


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, start_event=start_event)
        self.settings = settings.as_dict()
        self.input_classes = {}

    def get_ready(self):
        #Create empty settings object in which we will reconstruct our settings dictionary
        settings = HardwareMPSettings()
        settings.load_from_dict(self.settings)

        #Create appropriate classes here (note that when a sensodrive is created it will start its own process, whereas the keyboards and joysticks do not)
        for idx, keyboards in enumerate(self._sharedvalues_module.keyboards):
            self.input_classes[keyboards] = HardwareInputTypes.KEYBOARD.klass_mp(settings = settings.key_boards[idx],
                                                                                 shared_values = self._sharedvalues_module.keyboards[keyboards])

        for idx, joysticks in enumerate(self._sharedvalues_module.joysticks):
            self.input_classes[joysticks] = HardwareInputTypes.JOYSTICK.klass_mp(settings = settings.joy_sticks[idx],
                                                                                 shared_values = self._sharedvalues_module.joysticks[joysticks])


    def do_function(self):
        for inputs in self.input_classes:
            #will perform the mp input class for eaach available input
            self.input_classes[inputs].do()
