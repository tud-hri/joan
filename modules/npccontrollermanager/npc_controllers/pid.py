import math

from PyQt5 import QtWidgets
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes


class PIDControllerProcess:
    """
    Main class for the Keyboard input in a separate multiprocess, this will loop!. Make sure that the things you do
    in this class are serializable, else it will fail.
    """

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

        self._vehicle_id = ''

    def do(self):
        """
        Processes all the inputs of the keyboard input and writes them to self._data which is then written to the news
        in the action class
        :return: self._data a dictionary containing :
            self.shared_variables.brake = self.brake
            self.shared_variables.throttle = self.throttle
            self.shared_variables.steering_angle = self.steer
            self.shared_variables.handbrake = self.handbrake
            self.shared_variables.reverse = self.reverse
        """
        pass
        # TODO: implement this

    def _get_current_state(self):
        pass
        # TODO: implement a way to get the current state of the connected vehicle from shared variables


class PIDSettings:
    def __init__(self):
        self.controller_type = NPCControllerTypes.PID

        self.kp = 0.0
        self.kd = 0.0
        self.ki = 0.0

        # Steering Range
        self.min_steer = - math.pi / 2.
        self.max_steer = math.pi / 2.

    def as_dict(self):
        return self.__dict__

    def __str__(self):
        return str('PID Controller Settings')

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class PIDSettingsDialog(QtWidgets.QDialog):
    pass  # TODO implement
