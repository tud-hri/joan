from core.module_settings import ModuleSettings, find_settings_by_identifier
from modules.hardwaremanager.hardwaremanager_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules


class HardwareManagerSettings(ModuleSettings):
    """
    Contains the settings of the seperate hardware input types of the hardware manager module.
    """

    def __init__(self):
        """
        Initializes the inputs dictionary
        """
        super().__init__(JOANModules.HARDWARE_MANAGER)

        self.inputs = {}

    def reset(self):
        self.inputs = {}

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware ]
        manager has the unique property that multiple custom settings classes are combined in a list. This behavior is
        not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        self.reset()
        module_settings_to_load = loaded_dict[str(self.module)]

        for identifier, settings_dict in module_settings_to_load['inputs'].items():
            if 'Keyboard' in identifier:
                keyboard_settings = HardwareInputTypes.KEYBOARD.settings()
                keyboard_settings.set_from_loaded_dict(settings_dict)
                self.inputs[identifier] = keyboard_settings
            if 'Joystick' in identifier:
                joystick_settings = HardwareInputTypes.JOYSTICK.settings()
                joystick_settings.set_from_loaded_dict(settings_dict)
                self.inputs[identifier] = joystick_settings
            if 'SensoDrive' in identifier:
                sensodrive_settings = HardwareInputTypes.SENSODRIVE.settings()
                sensodrive_settings.set_from_loaded_dict(settings_dict)
                self.inputs[identifier] = sensodrive_settings

    def all_inputs(self):
        """
        Returns all input objects
        :return: all current objects in the inputs dictionary
        """
        return {**self.inputs}

    def add_hardware_input(self, input_type: HardwareInputTypes, input_settings=None):
        """
        Adds the hardware input settings
        :param input_type:
        :param input_settings:
        :return:
        """
        # create empty settings object
        if not input_settings:
            input_settings = input_type.settings()

            nr = 1
            name = '{0!s}_{1}'.format(input_type, nr)
            while name in self.inputs.keys():
                nr += 1
                name = '{0!s}_{1}'.format(input_type, nr)

            input_settings.identifier = name

        # add settings to dict, check if settings do not already exist
        if input_settings not in self.inputs.values():
            self.inputs[input_settings.identifier] = input_settings

        return input_settings

    def remove_hardware_input(self, identifier):
        """
        Removes the hardware input settings
        :param identifier:
        :return:
        """
        key, _ = find_settings_by_identifier(self.inputs, identifier)
        self.inputs.pop(key)
