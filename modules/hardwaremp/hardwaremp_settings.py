import math
from pathlib import Path

from PyQt5 import QtGui

from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class HardwareMPSettings(ModuleSettings):
    def __init__(self, settings_filename='./default_setting.json'):
        super().__init__(JOANModules.HARDWARE_MP)

        self.keyboards = []
        self.joysticks = []
        self.sensodrives = []

        if Path(settings_filename).is_file():
            self.load_from_file(settings_filename)
        else:
            self.save_to_file(settings_filename)

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """

        module_settings_to_load = loaded_dict[str(self.module)]

        # clean up existing settings
        while self.keyboards:
            device = self.keyboards.pop()
            del device
        while self.joysticks:
            device = self.joysticks.pop()
            del device
        while self.sensodrives:
            device = self.sensodrives.pop()
            del device

        self.keyboards = []
        for keyboard_settings_dict in module_settings_to_load['keyboards']:
            keyboard_settings = KeyBoardSettings()
            keyboard_settings.set_from_loaded_dict(keyboard_settings_dict)
            self.keyboards.append(keyboard_settings)

        self.joysticks = []
        for joystick_settings_dict in module_settings_to_load['joysticks']:
            joystick_settings = JoyStickSettings()
            joystick_settings.set_from_loaded_dict(joystick_settings_dict)
            self.joysticks.append(joystick_settings)

        self.sensodrives = []
        for sensodrive in module_settings_to_load['sensodrives']:
            sensodrive_settings = SensoDriveSettings()
            sensodrive_settings.set_from_loaded_dict(sensodrive)
            self.sensodrives.append(sensodrive_settings)

    def remove_hardware_input_device(self, setting):
        if isinstance(setting, KeyBoardSettings):
            self.keyboards.remove(setting)

        if isinstance(setting, JoyStickSettings):
            self.joysticks.remove(setting)

        if isinstance(setting, SensoDriveSettings):
            self.sensodrives.remove(setting)


class KeyBoardSettings:
    """
    Default keyboardinput settings that will load whenever a keyboardinput class is created.
    """

    def __init__(self):
        self.steer_left_key = QtGui.QKeySequence('a')[0]
        self.steer_right_key = QtGui.QKeySequence('d')[0]
        self.throttle_key = QtGui.QKeySequence('w')[0]
        self.brake_key = QtGui.QKeySequence('s')[0]
        self.reverse_key = QtGui.QKeySequence('r')[0]
        self.handbrake_key = QtGui.QKeySequence('space')[0]
        self.name = "Keyboard"

        # Steering Range
        self.min_steer = - 0.5 * math.pi
        self.max_steer = 0.5 * math.pi

        # Check auto center
        self.auto_center = True

        # Sensitivities
        self.steer_sensitivity = float(50.0)
        self.throttle_sensitivity = float(50.0)
        self.brake_sensitivity = float(50.0)

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class JoyStickSettings:
    """
    Default joystick settings that will load whenever a keyboardinput class is created.
    """

    def __init__(self):
        self.min_steer = -0.5 * math.pi
        self.max_steer = 0.5 * math.pi
        self.device_vendor_id = 0
        self.device_product_id = 0
        self.name = "Joystick"

        self.degrees_of_freedom = 12
        self.gas_channel = 9
        self.use_separate_brake_channel = False
        self.brake_channel = -1
        self.first_steer_channel = 0
        self.use_double_steering_resolution = True
        self.second_steer_channel = 1
        self.hand_brake_channel = 10
        self.hand_brake_value = 2
        self.reverse_channel = 10
        self.reverse_value = 8

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

    @staticmethod
    def get_preset_settings(device='default'):
        settings_to_return = JoyStickSettings()

        if device == 'xbox':
            settings_to_return.degrees_of_freedom = 12
            settings_to_return.gas_channel = 9
            settings_to_return.use_separate_brake_channel = False
            settings_to_return.brake_channel = -1
            settings_to_return.first_steer_channel = 0
            settings_to_return.use_double_steering_resolution = True
            settings_to_return.second_steer_channel = 1
            settings_to_return.hand_brake_channel = 10
            settings_to_return.hand_brake_value = 2
            settings_to_return.reverse_channel = 10
            settings_to_return.reverse_value = 8
        elif device == 'playstation':
            settings_to_return.degrees_of_freedom = 12
            settings_to_return.gas_channel = 9
            settings_to_return.use_separate_brake_channel = True
            settings_to_return.brake_channel = 8
            settings_to_return.first_steer_channel = 1
            settings_to_return.use_double_steering_resolution = False
            settings_to_return.second_steer_channel = -1
            settings_to_return.hand_brake_channel = 5
            settings_to_return.hand_brake_value = 40
            settings_to_return.reverse_channel = 6
            settings_to_return.reverse_value = 10

        return settings_to_return


class SensoDriveSettings:
    """
    Default sensodrive settings that will load whenever a keyboardinput class is created.
    """

    def __init__(self):
        self.endstops = math.radians(360.0)  # rad
        self.torque_limit_between_endstops = 200  # percent
        self.torque_limit_beyond_endstops = 200  # percent
        self.friction = 0  # Nm
        self.damping = 0.1  # Nm * s / rad
        self.spring_stiffness = 1  # Nm / rad
        self.torque = 0  # Nm

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
