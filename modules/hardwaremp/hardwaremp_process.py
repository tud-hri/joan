from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings= settings, start_event=start_event)

        self.shared_values = news.read_news(JOANModules.HARDWARE_MP)
        self.inputs = news.read_news('Inputs')
        self.settings = settings.as_dict()
        print(self.settings)
        self.input_classes = {}



    def get_ready(self):
        ## Create the classes here
        i = 0
        for items in self.inputs:
            if 'Keyboard' in items:
                self.input_classes[items] = HardwareInputTypes.KEYBOARD.MPklass(settings = self.settings['Hardware MP']['key_boards'][i], shared_values= self.inputs[items])
                i += 1




        # keyboardinput.hook(self.key_event, False)

    def do_function(self):
        for items in self.input_classes:
            self.input_classes[items].do()






