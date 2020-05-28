import inspect

from PyQt5 import QtGui
from enum import Enum

from process.joanmodulesettings import JoanModuleSettings
from modules.joanmodules import JOANModules


class HardWareManagerSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        super().__init__(module_enum)
        self.key_boards = []
        self.joy_sticks = []

    def set_from_loaded_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        try:
            module_settings_to_load = loaded_dict[str(self._module_enum)]
        except KeyError:
            warning_message = "WARNING: loading settings for the " + str(self._module_enum) + \
                              " module from a dictionary failed. The loaded dictionary did not contain " + str(self._module_enum) + " settings." + \
                              (" It did contain settings for: " + ", ".join(loaded_dict.keys()) if loaded_dict.keys() else "")
            print(warning_message)
            return

        self.key_boards = []
        for keyboard_settings_dict in module_settings_to_load['key_boards']:
            keyboard_settings = KeyBoardSettings()
            keyboard_settings.set_from_loaded_dict(keyboard_settings_dict)
            self.key_boards.append(keyboard_settings)

        self.joy_sticks = []
        for joystick_settings_dict in module_settings_to_load['joy_sticks']:
            joystick_settings = JoyStickSettings()
            joystick_settings.set_from_loaded_dict(joystick_settings_dict)
            self.joy_sticks.append(joystick_settings)


class KeyBoardSettings:
    def __init__(self):
        self.steer_left_key = QtGui.QKeySequence('a')[0]
        self.steer_right_key = QtGui.QKeySequence('d')[0]
        self.throttle_key = QtGui.QKeySequence('w')[0]
        self.brake_key = QtGui.QKeySequence('s')[0]
        self.reverse_key = QtGui.QKeySequence('r')[0]
        self.handbrake_key = QtGui.QKeySequence('space')[0]

        # Steering Range
        self.min_steer = -90
        self.max_steer = 90

        # Check auto center
        self.auto_center = True

        # Sensitivities
        self.steer_sensitivity = 50
        self.throttle_sensitivity = 50
        self.brake_sensitivity = 50

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class JoyStickSettings:
    def __init__(self):
        self.min_steer = -90
        self.max_steer = 90
        self.device_vendor_id = 0
        self.device_product_id = 0

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)