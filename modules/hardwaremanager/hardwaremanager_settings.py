import math
import multiprocessing as mp

from PyQt5 import QtGui

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

    def add_hardware_input(self, input_type, input_settings=None):

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


class KeyBoardSettings:
    """
    Default keyboardinput settings that will load whenever a keyboardinput class is created.
    """

    def __init__(self, identifier=''):
        self.steer_left_key = QtGui.QKeySequence('a')[0]
        self.steer_right_key = QtGui.QKeySequence('d')[0]
        self.throttle_key = QtGui.QKeySequence('w')[0]
        self.brake_key = QtGui.QKeySequence('s')[0]
        self.reverse_key = QtGui.QKeySequence('r')[0]
        self.handbrake_key = QtGui.QKeySequence('space')[0]
        self.identifier = identifier
        self.input_type = HardwareInputTypes.KEYBOARD.value
        # self.input_name = '{0!s} {1!s}'.format(HardwareInputTypes.KEYBOARD, str(self.identifier))

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

    def __init__(self, identifier=''):
        self.min_steer = -0.5 * math.pi
        self.max_steer = 0.5 * math.pi
        self.device_vendor_id = 0
        self.device_product_id = 0
        self.identifier = identifier
        self.input_type = HardwareInputTypes.JOYSTICK.value
        # self.input_name = '{0!s} {1!s}'.format(HardwareInputTypes.JOYSTICK, str(self.identifier))

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

    def __init__(self, identifier=''):
        self.endstops = math.radians(360.0)  # rad
        self.torque_limit_between_endstops = 200  # percent
        self.torque_limit_beyond_endstops = 200  # percent
        self.friction = 0  # Nm
        self.damping = 0.1  # Nm * s / rad
        self.spring_stiffness = 1  # Nm / rad
        self.torque = 0  # Nm
        self.identifier = identifier
        self.input_type = HardwareInputTypes.SENSODRIVE.value
        # self.input_name = '{0!s} {1!s}'.format(HardwareInputTypes.SENSODRIVE, str(self.identifier))

        self.turn_on_event = mp.Event()
        self.turn_off_event = mp.Event()
        self.clear_error_event = mp.Event()
        self.close_event = mp.Event()

        self.state_queue = mp.Queue()

        self.current_state = 0x00

        self.settings_dict = {}

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

    def settings_dict_for_pipe(self):
        self.settings_dict = {'endstops': self.endstops,  # rad
                              'torque_limit_between_endstops': self.torque_limit_between_endstops,  # percent
                              'torque_limit_beyond_endstops': self.torque_limit_beyond_endstops,  # percent
                              'friction': self.friction,  # Nm
                              'damping': self.damping,  # Nm * s / rad
                              'spring_stiffness': self.spring_stiffness,  # Nm / rad
                              'torque': self.torque,  # Nm
                              'identifier': self.identifier}

        return self.settings_dict
