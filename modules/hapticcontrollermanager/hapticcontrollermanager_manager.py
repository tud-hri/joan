from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from .hapticcontrollermanager_controllertypes import HapticControllerTypes


class HapticControllerManager(ModuleManager):
    """HapticControllerManager keeps track of which haptic controllers are being used with what settings. """

    def __init__(self, news, central_settings, signals, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.HAPTIC_CONTROLLER_MANAGER, news=news, central_settings=central_settings, signals=signals,
                         time_step_in_ms=time_step_in_ms, parent=parent)
        self._haptic_controllers = {}
        self.haptic_controller_type = None
        self.haptic_controller_settings = None

    def initialize(self):
        super().initialize()
        for haptic_controller in self.module_settings.haptic_controllers.values():
            self.shared_variables.haptic_controllers[haptic_controller.identifier] = HapticControllerTypes(
                haptic_controller.haptic_controller_type).shared_variables()

    def get_ready(self):
        super().get_ready()

    def load_from_file(self, settings_file_to_load):
        # remove all settings from the dialog
        for haptic_controller in self.module_settings.all_haptic_controllers().values():
            self.remove_haptic_controller(haptic_controller.identifier)

        # load settings from file into module_settings object
        self.module_settings.load_from_file(settings_file_to_load)

        # add all settings tp module_dialog
        from_button = False
        for haptic_controller_settings in self.module_settings.all_haptic_controllers().values():
            self.add_haptic_controller(HapticControllerTypes(haptic_controller_settings.haptic_controller_type), from_button, haptic_controller_settings)

    def add_haptic_controller(self, haptic_controller_type: HapticControllerTypes, from_button, haptic_controller_settings=None):
        # add to module_settings
        haptic_controller_settings = self.module_settings.add_haptic_controller(haptic_controller_type, haptic_controller_settings)

        # add to module_dialog
        self.module_dialog.add_haptic_controller(haptic_controller_settings, from_button)

    def remove_haptic_controller(self, identifier):
        # remove from settings
        self.module_settings.remove_haptic_controller(identifier)

        # remove settings from dialog
        self.module_dialog.remove_haptic_controller(identifier)
