from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes


class NPCControllerManagerSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.NPC_CONTROLLER_MANAGER)

        self.controllers = {}

    def reset(self):
        self.controllers = {}

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because the NPC controller manager has the unique property
        that multiple custom settings objects are combined in a dictionary. This behavior is not supported by the normal joan module settings, so a specific
        solution to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        self.reset()
        module_settings_to_load = loaded_dict[str(self.module)]

        for identifier, settings_dict in module_settings_to_load['controllers'].items():
            if str(NPCControllerTypes.PURE_PURSUIT) in identifier:
                pp_controller_settings = NPCControllerTypes.PURE_PURSUIT.settings()
                pp_controller_settings.set_from_loaded_dict(settings_dict)
                self.controllers[identifier] = pp_controller_settings

    def all_controllers(self):
        return {**self.controllers}

    def add_new_controller(self, controller_type: NPCControllerTypes):
        controller_settings = controller_type.settings()

        nr = 1
        identifier = '{0!s}_{1}'.format(controller_type, nr)
        while identifier in self.controllers.keys():
            nr += 1
            identifier = '{0!s}_{1}'.format(controller_type, nr)

        self.controllers[identifier] = controller_settings
        return identifier, controller_settings

    def remove_controller(self, identifier):
        self.controllers.pop(identifier)
