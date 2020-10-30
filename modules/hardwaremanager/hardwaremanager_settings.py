from core.module_settings import ModuleSettings, find_settings_by_identifier
from modules.hardwaremanager.hardwaremanager_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules


class HardwareMPSettings(ModuleSettings):
    """
    Contains the settings of the seperate hardware input types of the hardware manager module.
    """

    def __init__(self):
        super().__init__(JOANModules.HARDWARE_MP)

        self.keyboards = {}
        self.joysticks = {}
        self.sensodrives = {}

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """

        module_settings_to_load = loaded_dict[str(self.module)]

        self.keyboards = {}
        for identifier, settings_dict in module_settings_to_load['keyboards'].items():
            keyboard_settings = HardwareInputTypes.KEYBOARD.settings()
            keyboard_settings.set_from_loaded_dict(settings_dict)
            self.keyboards.update({identifier: keyboard_settings})

        self.joysticks = {}
        for identifier, settings_dict in module_settings_to_load['joysticks'].items():
            joystick_settings = HardwareInputTypes.JOYSTICK.settings()
            joystick_settings.set_from_loaded_dict(settings_dict)
            self.joysticks.update({identifier: joystick_settings})

        self.sensodrives = {}
        for identifier, settings_dict in module_settings_to_load['sensodrives'].items():
            sensodrive_settings = HardwareInputTypes.SENSODRIVE.settings()
            sensodrive_settings.set_from_loaded_dict(settings_dict)
            self.sensodrives.update({identifier: sensodrive_settings})

    def all_inputs(self):
        return {**self.keyboards, **self.joysticks, **self.sensodrives}

    def add_hardware_input(self, input_type: HardwareInputTypes, input_settings=None):

        # select the dict corresponding to the input_type
        input_type_dict = None
        if input_type == HardwareInputTypes.KEYBOARD:
            input_type_dict = self.keyboards
        elif input_type == HardwareInputTypes.JOYSTICK:
            input_type_dict = self.joysticks
        elif input_type == HardwareInputTypes.SENSODRIVE:
            input_type_dict = self.sensodrives
        else:
            # HardwareInputTypes unknown, return empty handed
            return None

        # create empty settings object
        if not input_settings:
            input_settings = input_type.settings()

            nr = 1
            name = '{0!s}_{1}'.format(input_type, nr)
            while name in input_type_dict.keys():
                nr += 1
                name = '{0!s}_{1}'.format(input_type, nr)

            input_settings.identifier = name

        # add settings to dict, check if settings do not already exist
        if input_settings not in input_type_dict.values():
            input_type_dict[input_settings.identifier] = input_settings

        return input_settings

    def remove_hardware_input(self, identifier):
        if str(HardwareInputTypes.KEYBOARD) in identifier:
            key, _ = find_settings_by_identifier(self.keyboards, identifier)
            self.keyboards.pop(key)

        if str(HardwareInputTypes.JOYSTICK) in identifier:
            key, _ = find_settings_by_identifier(self.joysticks, identifier)
            self.joysticks.pop(key)

        if str(HardwareInputTypes.SENSODRIVE) in identifier:
            key, _ = find_settings_by_identifier(self.sensodrives, identifier)
            self.sensodrives.pop(key)
