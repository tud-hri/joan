import inspect
import math
from enum import Enum

from PyQt5 import QtGui

from modules.joanmodules import JOANModules
from core.joanmodulesettings import JoanModuleSettings


class HardwareManagerSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        super().__init__(module_enum)

        self.key_boards = []
        self.joy_sticks = []
        self.sensodrives = []

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        # prepare the module for the new settings
        self.before_load_settings.emit()

        module_settings_to_load = loaded_dict[str(self._module_enum)]

        # clean up existing settings
        while self.key_boards:
            device = self.key_boards.pop()
            del device
        while self.joy_sticks:
            device = self.joy_sticks.pop()
            del device
        while self.sensodrives:
            device = self.sensodrives.pop()
            del device

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

        self.sensodrives = []
        for sensodrive in module_settings_to_load['sensodrives']:
            sensodrive_settings = SensoDriveSettings()
            sensodrive_settings.set_from_loaded_dict(sensodrive)
            self.sensodrives.append(sensodrive_settings)

        # done loading settings, emit signal
        self.load_settings_done.emit()

    def remove_input_device(self, name):
        if "Keyboard" in name:
            for device in self.key_boards:
                if device.name == name:
                    self.key_boards.remove(device)

        if "Joystick" in name:
            for device in self.joy_sticks:
                if device.name == name:
                    self.joy_sticks.remove(device)

        if "SensoDrive" in name:
            for device in self.sensodrives:
                if device.name == name:
                    self.sensodrives.remove(device)

    @staticmethod
    def _copy_dict(source, destination):
        for key, value in source.items():
            if isinstance(value, list):
                destination[key] = HardwareManagerSettings._copy_list(value)
            elif isinstance(value, dict):
                try:
                    destination[key]  # make sure that the destination dict has an entry at key
                except KeyError:
                    destination[key] = dict()
                HardwareManagerSettings._copy_dict(value, destination[key])
            elif hasattr(value, '__dict__') and not isinstance(value, Enum) and not inspect.isclass(value):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    destination[key] = value.as_dict()
                except NotImplementedError:
                    destination[key] = dict()
                    HardwareManagerSettings._copy_dict(value.__dict__, destination[key])
            else:
                destination[key] = source[key]

    @staticmethod
    def _copy_list(source):
        output_list = []
        for index, item in enumerate(source):
            if isinstance(item, list):
                output_list.append(HardwareManagerSettings._copy_list(item))
            elif hasattr(item, '__dict__') and not isinstance(item, Enum) and not inspect.isclass(item):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    output_list.append(item.as_dict())
                except NotImplementedError:
                    output_list.append(dict())
                    HardwareManagerSettings._copy_dict(item.__dict__, output_list[index])
            else:
                output_list.append(item)
        return output_list


class KeyBoardSettings:
    """
    Default keyboard settings that will load whenever a keyboard class is created.
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
    """
    Default joystick settings that will load whenever a keyboard class is created.
    """

    def __init__(self):
        self.min_steer = -90
        self.max_steer = 90
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
    Default sensodrive settings that will load whenever a keyboard class is created.
    """

    def __init__(self):
        self.endstops = math.radians(360.0)         # rad
        self.torque_limit_between_endstops = 200    # percent
        self.torque_limit_beyond_endstops = 200     # percent
        self.friction = 0                           # Nm
        self.damping = 0                            # Nm * s / rad
        self.spring_stiffness = 0                   # Nm / rad
        self.torque = 0                             # Nm

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
