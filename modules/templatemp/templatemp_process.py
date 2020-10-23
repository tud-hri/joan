from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from datetime import datetime


class TemplateMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event, exception_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, start_event=start_event, exception_event=exception_event)

        # it is possible to read from other modules
        # do NOT WRITE to other modules' news to prevent spaghetti-code
        self.shared_variables_hardware = news.read_news(JOANModules.HARDWARE_MP)

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings ar converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        super().get_ready()
        now = datetime.now()

        # the settings-key 'overwrite_with_current_time' will be used as key
        self._module_shared_variables.overwrite_with_current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # show current shared values for this module
        print(self._module_shared_variables.__dict__)

        # show current shared_variables for another module
        print(self.shared_variables_hardware.__dict__)

    def do(self):
        """
        do something and write the result in a shared_variable
        """
        now = datetime.now()
        self._module_shared_variables.overwrite_with_current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # show current time
        print(self._module_shared_variables.overwrite_with_current_time)

        # try the brake-key (the default key for brake is 's')
        for _, value in self.shared_variables_hardware.keyboards.items():
            print("brake %s" % value.brake)
