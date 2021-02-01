from core.module_settings import ModuleSettings, find_settings_by_identifier
from modules.joanmodules import JOANModules
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes


class HapticControllerManagerSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.HAPTIC_CONTROLLER_MANAGER)
        self.haptic_controllers = {}

    def reset(self):
        self.haptic_controllers = {}

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        self.reset()
        module_settings_to_load = loaded_dict[str(self.module)]

        for identifier, settings_dict in module_settings_to_load['haptic_controllers'].items():
            if 'FDCA' in identifier:
                ego_vehicle_settings = HapticControllerTypes.FDCA.settings()
                ego_vehicle_settings.set_from_loaded_dict(settings_dict)
                self.haptic_controllers.update({identifier: ego_vehicle_settings})

    def add_haptic_controller(self, haptic_controller_type: HapticControllerTypes, haptic_controller_settings=None):
        """
        :param haptic_controller_type: enum, see hapticcontrollertypes.py
        :param haptic_controller_settings: settings objects
        :return:
        """
        # create empty settings object
        if not haptic_controller_settings:
            haptic_controller_settings = haptic_controller_type.settings()

            nr = 1
            name = '{0!s}_{1}'.format(haptic_controller_type, nr)
            while name in self.haptic_controllers.keys():
                nr += 1
                name = '{0!s}_{1}'.format(haptic_controller_type, nr)

            haptic_controller_settings.identifier = name

        # add settings to dict, check if settings do not already exist
        if haptic_controller_settings not in self.haptic_controllers.values():
            self.haptic_controllers[haptic_controller_settings.identifier] = haptic_controller_settings

        return haptic_controller_settings

    def all_haptic_controllers(self):
        return {**self.haptic_controllers}

    def remove_haptic_controller(self, identifier):
        key, _ = find_settings_by_identifier(self.haptic_controllers, identifier)
        self.haptic_controllers.pop(key)
