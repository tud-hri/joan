from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from datetime import datetime


class TemplateProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)

        # it is possible to read from other modules
        # do_while_running NOT WRITE to other modules' news to prevent spaghetti-code
        self.shared_variables_hardware = news.read_news(JOANModules.HARDWARE_MANAGER)
        self.shared_variables_carlainterface = news.read_news(JOANModules.CARLA_INTERFACE)

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings ar converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        now = datetime.now()

        # the settings-key 'overwrite_with_current_time' will be used as key
        self._module_shared_variables.overwrite_with_current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def do_while_running(self):
        """
        do_while_running something and write the result in a shared_variable
        """
        now = datetime.now()
        self._module_shared_variables.overwrite_with_current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
