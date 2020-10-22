from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class TemplateMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings = settings, start_event=start_event)

        self.shared_values_hardware = news.read_news(JOANModules.HARDWARE_MP)





    def do_function(self):
        try:
            print(self.shared_values_hardware.joysticks['Joystick 0'].throttle, self.shared_values_hardware.keyboards['Keyboard 0'].throttle)
        except:
            pass
        # try:
        #     print(self.shared_values_hardware.keyboardtest.brake)
        # except:
        #     pass