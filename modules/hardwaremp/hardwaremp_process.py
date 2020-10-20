from core.module_process import ModuleProcess
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, start_event=start_event)

        # het kan dus via attributes
        print("direct via een attribute:", self._sharedvalues_module.keyboardtest.brake)
        # of (zelfde, maar dan anders; getattr(x, 'foobar') is equivalent to x.foobar):
        print("of via getattr: ", getattr(self._sharedvalues_module, 'keyboardtest2').brake)

        # of, als derde optie zouden we ook via een dict kunnen doen:
        print("of met een dict:", self._sharedvalues_module.keyboards["keyboard3"].brake)

        self.settings = settings.as_dict()
        self.input_classes = {}

    def get_ready(self):
        ## Create the classes here
        # i = 0
        # for items in self.inputs:
        #     if 'Keyboard' in items:
        #         self.input_classes[items] = HardwareInputTypes.KEYBOARD.MPklass(settings=self.settings['Hardware MP']['key_boards'][i],
        #                                                                         shared_values=self.inputs[items])
        #         i += 1
        i = 0
        for items in self._sharedvalues_module.keyboards:
            self.input_classes[items] = HardwareInputTypes.KEYBOARD.mpklass(settings = self.settings['Hardware MP']['key_boards'][i], shared_values = self._sharedvalues_module.keyboards[items])
            i+= 1

        # keyboardinput.hook(self.key_event, False)

    def do_function(self):
        for inputs in self.input_classes:
            self.input_classes[inputs].do()
