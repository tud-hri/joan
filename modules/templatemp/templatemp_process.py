from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from datetime import datetime


class TemplateMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, start_event=start_event)
        self.shared_values = news.read_news(JOANModules.TEMPLATE_MP)

        # it is possible to read from other modules
        # do NOT WRITE to other modules' news to prevent spagetti-code
        self.shared_values_hardware = news.read_news(JOANModules.HARDWARE_MP)

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings ar converted to type dict
        The super().get_ready() method converts the module_settings back to object
        You can change values for this module (in this case: TemplateMPSettings)
        and write to shared memory, using the settings-key as news-key, so data can be recorded/plotted
        """
        super().get_ready()
        now = datetime.now()

        # the settings-key 'overwrite_with_current_time' will be used as key 
        self.shared_values.overwrite_with_current_time = bytes(now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], 'utf-8')

        # show current shared values for this module
        print(self.shared_values.__dict__)

        # show current shared_values for another module
        print(self.shared_values_hardware.__dict__)

    def do_function(self):
        """
        do something and write the result in a shared_variable
        """
        now = datetime.now()
        self.shared_values.overwrite_with_current_time = bytes(now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], 'utf-8')
       
        # show current time
        print(self.shared_values.overwrite_with_current_time)

        # try the brake-key (the default key for brake is 's')
        for _, value in self.shared_values_hardware.keyboards.items():
            print("brake %s" % value.brake)
