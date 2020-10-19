from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from modules.hardwaremp.hardwaremp_inputclasses.keyboardinput.joankeyboardMP import JOANKeyboardMP


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings= settings, start_event=start_event)

        self.shared_values = news.read_news(JOANModules.HARDWARE_MP)
        self.settings = settings.as_dict()


    def get_ready(self):
        ## Create the class here
        for items in self.settings['Hardware MP']['key_boards']:
            self.Keyboard1 = JOANKeyboardMP(items, self.shared_values)


        # keyboardinput.hook(self.key_event, False)

    def do_function(self):
        if hasattr(self, 'Keyboard1'):
            self.Keyboard1.do()



