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
        mp_settings = settings.loadfrom_dict(self.settings)
        print(mp_settings)

        #Create appropriate classes here (note that when a sensodrive is created it will start its own process, whereas the keyboards and joysticks do not)
        i = 0
        j = 0
        k = 0
        for keyboards in self._sharedvalues_module.keyboards:
            self.input_classes[keyboards] = HardwareInputTypes.KEYBOARD.klass_mp(settings = self.settings['Hardware MP']['key_boards'][i],
                                                                                 shared_values = self._sharedvalues_module.keyboards[keyboards])
            i += 1

        for joysticks in self._sharedvalues_module.joysticks:
            self.input_classes[joysticks] = HardwareInputTypes.JOYSTICK.klass_mp(settings = self.settings['Hardware MP']['joy_sticks'][j],
                                                                                 shared_values = self._sharedvalues_module.joysticks[joysticks])
            j += 1


    def do_function(self):
        for inputs in self.input_classes:
            #will perform the mp input class for eaach available input
            self.input_classes[inputs].do()
