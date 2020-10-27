import math
import multiprocessing as mp

from PyQt5 import QtGui

from core.module_settings import ModuleSettings
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules
import queue

class HardwareMPSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.HARDWARE_MP)

        self.keyboards = {}
        self.joysticks = {}
        self.sensodrives = {}

        # TODO: autoloading of settings need to be fixed, but not here in the settings object; it screws up the settings translation in process.
        # if Path(settings_filename).is_file():
        #     self.load_from_file(settings_filename)
        # else:
        #     self.save_to_file(settings_filename)

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
        # while self.keyboards:
        #     device = self.keyboards.pop()  # TODO: comment uit en maybe is het nodig maybe not
        #     del device
        # while self.joysticks:
        #     device = self.joysticks.pop()
        #     del device
        # while self.sensodrives:
        #     device = self.sensodrives.pop()
        #     del device

        # TODO Maak hier van de lists -> dicts; eerste stap gezet, moet gechecked worden
        self.keyboards = {}
        for identifier, settings_dict in module_settings_to_load['keyboards'].items():
            keyboard_settings = KeyBoardSettings()
            keyboard_settings.set_from_loaded_dict(settings_dict)
            self.keyboards.update({identifier: keyboard_settings})

        self.joysticks = {}
        for identifier, settings_dict in module_settings_to_load['joysticks'].items():
            joystick_settings = JoyStickSettings()
            joystick_settings.set_from_loaded_dict(settings_dict)
            self.joysticks.update({identifier: joystick_settings})

        self.sensodrives = {}
        for identifier, settings_dict in module_settings_to_load['sensodrives'].items():
            sensodrive_settings = SensoDriveSettings()
            sensodrive_settings.set_from_loaded_dict(settings_dict)
            self.sensodrives.update({identifier: sensodrive_settings})

    def remove_hardware_input_device(self, setting):
        # TODO dit ook naar dict; eerste stap gemaakt, moet gechecked worden
        if isinstance(setting, KeyBoardSettings):
            self.keyboards.pop(setting.identifier)

        if isinstance(setting, JoyStickSettings):
            self.joysticks.pop(setting.identifier)

        if isinstance(setting, SensoDriveSettings):
            self.sensodrives.pop(setting.identifier)


class KeyBoardSettings:
    """
    Default keyboardinput settings that will load whenever a keyboardinput class is created.
    """

    def __init__(self, input_type: HardwareInputTypes = HardwareInputTypes.KEYBOARD, identifier = 0):  # TODO Use identifier integer
        self.steer_left_key = QtGui.QKeySequence('a')[0]
        self.steer_right_key = QtGui.QKeySequence('d')[0]
        self.throttle_key = QtGui.QKeySequence('w')[0]
        self.brake_key = QtGui.QKeySequence('s')[0]
        self.reverse_key = QtGui.QKeySequence('r')[0]
        self.handbrake_key = QtGui.QKeySequence('space')[0]
        self.identifier = identifier
        self.input_type = input_type

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

    def __init__(self, input_type: HardwareInputTypes = HardwareInputTypes.JOYSTICK, identifier = 0):
        self.min_steer = -0.5 * math.pi
        self.max_steer = 0.5 * math.pi
        self.device_vendor_id = 0
        self.device_product_id = 0
        self.identifier = identifier
        self.input_type = input_type

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

    def __init__(self, input_type: HardwareInputTypes = HardwareInputTypes.SENSODRIVE, identifier = 0):
        self.endstops = math.radians(360.0)  # rad
        self.torque_limit_between_endstops = 200  # percent
        self.torque_limit_beyond_endstops = 200  # percent
        self.friction = 0  # Nm
        self.damping = 0.1  # Nm * s / rad
        self.spring_stiffness = 1  # Nm / rad
        self.torque = 0  # Nm
        self.identifier = identifier


        self.turn_on_event = mp.Event()
        self.turn_off_event = mp.Event()
        self.clear_error_event = mp.Event()
        self.close_event = mp.Event()

        self.state_queue = mp.Queue()
        self.input_type = input_type

        self.current_state = 0x00

        self.settings_dict = {}



    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

    def settings_dict_for_pipe(self):
        self.settings_dict = {'endstops': self.endstops, # rad
                              'torque_limit_between_endstops': self.torque_limit_between_endstops,  # percent
                              'torque_limit_beyond_endstops': self.torque_limit_beyond_endstops,    # percent
                              'friction': self.friction,                                            # Nm
                              'damping': self.damping,                                              # Nm * s / rad
                              'spring_stiffness': self.spring_stiffness,                            # Nm / rad
                              'torque': self.torque,                                                # Nm
                              'identifier': self.identifier}

        return self.settings_dict


