import inspect
from enum import Enum


class HardWareManagerSettings:
    def __init__(self):
        self.key_boards = []
        self.joy_sticks = []
        self.sensodrives = []

    def set_from_loaded_dict(self, loaded_dict):
        #  TODO: write more general and robust version
        self.key_boards = []
        for keyboard in loaded_dict['key_boards']:
            keyboard_settings = KeyBoardSettings()
            keyboard_settings.set_from_loaded_dict(keyboard)
            self.key_boards.append(keyboard_settings)

        self.joy_sticks = []
        for joystick in loaded_dict['joy_sticks']:
            joystick_settings = JoyStickSettings()
            joystick_settings.set_from_loaded_dict(joystick)
            self.joy_sticks.append(joystick_settings)

        self.sensodrives = []
        for sensodrive in loaded_dict['sensodrives']:
            sensodrive_settings = SensoDriveSettings()
            sensodrive_settings.set_from_loaded_dict(sensodrive)
            self.sensodrives.append(sensodrive_settings)

    def as_dict(self):
        output_dict = {}
        self._copy_dict(self.__dict__, output_dict)
        return output_dict

    @staticmethod
    def _copy_dict(source, destination):
        for key, value in source.items():
            if isinstance(value, list):
                destination[key] = HardWareManagerSettings._copy_list(value)
            elif isinstance(value, dict):
                try:
                    destination[key]  # make sure that the destination dict has an entry at key
                except KeyError:
                    destination[key] = dict()
                HardWareManagerSettings._copy_dict(value, destination[key])
            elif hasattr(value, '__dict__') and not isinstance(value, Enum) and not inspect.isclass(value):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    destination[key] = value.as_dict()
                except NotImplementedError:
                    destination[key] = dict()
                    HardWareManagerSettings._copy_dict(value.__dict__, destination[key])
            else:
                destination[key] = source[key]

    @staticmethod
    def _copy_list(source):
        output_list = []
        for index, item in enumerate(source):
            if isinstance(item, list):
                output_list.append(HardWareManagerSettings._copy_list(item))
            elif hasattr(item, '__dict__') and not isinstance(item, Enum) and not inspect.isclass(item):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    output_list.append(item.as_dict())
                except NotImplementedError:
                    output_list.append(dict())
                    HardWareManagerSettings._copy_dict(item.__dict__, output_list[index])
            else:
                output_list.append(item)
        return output_list


class KeyBoardSettings:
    def __init__(self):
        self.steer_left_key = 'a'
        self.steer_right_key = 'd'
        self.throttle_key = 'w'
        self.brake_key = 's'
        self.reverse_key = 'r'
        self.handbrake_key = 'space'

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

class SensoDriveSettings:
    def __init__(self):
        self.endstops = 360                    # degrees
        self.torque_limit_between_endstop = 20 # percent
        self.torque_limit_beyond_endstop = 20  # percent
        self.friction = 300                    # mNm
        self.damping = 30                      # mNm/rev/min
        self.spring_stiffness = 20             # mNm/deg
   

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
