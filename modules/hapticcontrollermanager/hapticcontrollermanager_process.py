from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes


class HapticControllerManagerProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)

        # it is possible to read from other modules
        # do_while_running NOT WRITE to other modules' news to prevent spaghetti-code
        self.shared_variables_hardware = news.read_news(JOANModules.HARDWARE_MANAGER)
        self.shared_variables_carla_interface = news.read_news(JOANModules.CARLA_INTERFACE)
        self.settings_carla_interface = settings_singleton.get_settings(JOANModules.CARLA_INTERFACE)

        self.haptic_controller_objects = {}

    def get_ready(self):
        for key, value in self._settings_as_object.haptic_controllers.items():
            self.haptic_controller_objects[key] = HapticControllerTypes(value.haptic_controller_type).process(settings=value,
                                                                                                              shared_variables=self._module_shared_variables.haptic_controllers[
                                                                                                                  key], carla_interface_settings=self.settings_carla_interface)
        """
        When instantiating the ModuleProcess, the settings ar converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        pass

    def do_while_running(self):
        """
        do_while_running something and write the result in a shared_variable
        """
        for haptic_controllers in self.haptic_controller_objects:
            # will perform the mp input class for eaach available input
            self.haptic_controller_objects[haptic_controllers].do(carlainterface_shared_variables=self.shared_variables_carla_interface,
                                                                  hardware_manager_shared_variables=self.shared_variables_hardware,
                                                                  carla_interface_settings=self.settings_carla_interface)
        pass
