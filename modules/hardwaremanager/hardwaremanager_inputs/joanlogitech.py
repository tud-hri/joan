import math
import os
import logitech_steering_wheel as lsw

from PyQt5 import QtWidgets, QtGui, uic
from modules.hardwaremanager.hardwaremanager_inputtypes import HardwareInputTypes


class JOANLogitechSteeringWheelProcess:

    def __init__(self, settings, shared_variables):
        self.settings = settings

        self.shared_variables = shared_variables

        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False
        self._data = {}
        self._is_connected = False
        lsw.update()

    def do(self):
        if not self._is_connected:
            lsw.initialize_with_window(True, self.settings.window_id)
            self._is_connected = lsw.is_connected(self.settings.steering_wheel_index)

            if not self._is_connected:
                raise RuntimeError('Could not connect to steering wheel ' + str(self.settings.steering_wheel_index) +
                                   '. Make sure you initialize the logitech steering wheel sdk before creating a SteeringWheelAgent object.')
            else:
                print('Logitech Steering Wheel %d connected' % self.settings.steering_wheel_index)

        lsw.update()
        state = lsw.get_state(self.settings.steering_wheel_index)

        print(state.lY)
        print(state.lRz)
        print(state.lX)
        return

        # Throttle:
        throttle = (2 ** 15 - state.lY)
        throttle /= 2 ** 16

        # Brake:
        brake = (2 ** 15 - state.lRz)
        brake /= 2 ** 16

        # Steering:
        steering = (2 ** 15 / 2 - state.lX)
        steering /= 2 ** 16

        handbrake = state.rgbButtons[0]
        reverse = state.rgbButtons[1]

        # Set the shared variables again:
        self.shared_variables.brake = brake
        self.shared_variables.throttle = throttle
        self.shared_variables.steering_angle = steering
        self.shared_variables.handbrake = handbrake
        self.shared_variables.reverse = reverse


class LogitechSteeringWheelSettings:
    """
    Default settings that will load whenever a steering wheel is initialized.
    """

    def __init__(self, identifier=''):
        self.identifier = identifier
        self.input_type = HardwareInputTypes.LOGITECH_STEERING_WHEEL.value

        self.steering_wheel_index = 0
        self.window_id = 0

    def as_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.identifier)

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class LogitechSteeringWheelSettingsDialog(QtWidgets.QDialog):
    """
    Class for the settings Dialog of a keyboardinput, this class should pop up whenever it is asked by the user or when
    creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
    """

    def __init__(self, module_manager=None, settings=None, parent=None):
        """
        Initializes the settings dialog with the appropriate keyboardinput settings
        :param settings:
        :param parent:
        """
        super().__init__(parent)

    def display_values(self, settings_to_display=None):
        pass
