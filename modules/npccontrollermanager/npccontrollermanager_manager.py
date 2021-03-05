from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from modules.npccontrollermanager.npccontrollermanager_settings import NPCControllerManagerSettings
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes


class NPCControllerManager(ModuleManager):
    module_settings: NPCControllerManagerSettings

    def __init__(self, news, central_settings, signals, central_state_monitor, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.NPC_CONTROLLER_MANAGER, news=news, central_settings=central_settings,
                         signals=signals, central_state_monitor=central_state_monitor, time_step_in_ms=time_step_in_ms, parent=parent)
        self.controller_identifiers = []

    def initialize(self):
        """
        Initializes the manager, executes when transitioning from the Stopped State.
        :return:
        """
        super().initialize()
        for identifier, controller_settings in self.module_settings.controllers.items():
            self.shared_variables.controllers[identifier] = controller_settings.controller_type.shared_variables()

    def load_from_file(self, settings_file_to_load):
        for controller_identifier in self.all_controller_identifiers:
            self.remove_controller(controller_identifier)

        # load settings from file into module_settings object
        self.module_settings.load_from_file(settings_file_to_load)

        # add all settings tp module_dialog
        for controller_settings in self.module_settings.all_controllers().values():
            self.module_dialog.add_controller(controller_settings)

    def add_controller(self, controller_type: NPCControllerTypes, show_settings_dialog=False):
        identifier, controller_settings = self.module_settings.add_new_controller(controller_type)
        self.module_dialog.add_controller(identifier, controller_settings, show_settings_dialog)

    def remove_controller(self, identifier):
        self.module_settings.remove_controller(identifier)
        self.module_dialog.remove_controller(identifier)

    @property
    def all_controller_identifiers(self):
        return list(self.module_settings.all_controllers().keys())
