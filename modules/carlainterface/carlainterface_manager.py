from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class CarlaInterfaceManager(ModuleManager):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.CARLA_INTERFACE, time_step_in_ms=time_step_in_ms, parent=parent)

        print(self.singleton_settings.all_settings)

    def update_shared_variables_adjustable_settings(self):
        # update value in self.shared_variables with the value in settings
        self.shared_variables.overwrite_with_current_time = self.module_settings.overwrite_with_current_time

