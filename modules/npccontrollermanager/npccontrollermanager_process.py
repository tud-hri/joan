from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class NPCControllerManagerProcess(ModuleProcess):
    """
    Overall process that inherits from ModuleProcess (will loop at the desired frequency)
    """

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)
        self.daemon = False
        self.controller_sub_processes = {}
        self.news = news

    def get_ready(self):
        """
        Is automatically called when transitioning to the ready state. Initializes all controller sub-processes.
        """
        for key, value in self._settings_as_object.controllers.items():
            self.controller_sub_processes[key] = value.controller_type.process(settings=value,
                                                                               shared_variables=self._module_shared_variables.controllers[key],
                                                                               carla_interface_shared_variables=self.news.read_news(JOANModules.CARLA_INTERFACE)
                                                                               )
            self.controller_sub_processes[key].get_ready()

    def do_while_running(self):
        """
        Loops when the module is running on the rate defined by the time_step_in_ms.
        :return:
        """
        for _, controller in self.controller_sub_processes.items():
            controller.do()
