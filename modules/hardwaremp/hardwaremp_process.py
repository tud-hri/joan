from core.module_process import ModuleProcess
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, start_event=start_event)
        self.settings = settings.as_dict()
        self.input_classes = {}

    def get_ready(self):
        #Create appropriate classes here
        i = 0
        for items in self._sharedvalues_module.keyboards:
            self.input_classes[items] = HardwareInputTypes.KEYBOARD.klass_mp(settings = self.settings['Hardware MP']['key_boards'][i], shared_values = self._sharedvalues_module.keyboards[items])
            i+= 1

        # keyboardinput.hook(self.key_event, False)

    def do_function(self):
        for inputs in self.input_classes:
            self.input_classes[inputs].do()
