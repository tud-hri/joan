import math
import os
import numpy as np

from PyQt5 import QtWidgets
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes
from modules.npccontrollermanager.npccontrollermanager_sharedvariables import NPCControllerSharedVariables


class PIDControllerProcess:
    """
    Main class for the Keyboard input in a separate multiprocess, this will loop!. Make sure that the things you do
    in this class are serializable, else it will fail.
    """

    def __init__(self, settings, shared_variables: NPCControllerSharedVariables, carla_interface_shared_variables):
        self.settings = settings
        self.shared_variables = shared_variables
        self.carla_interface_shared_variables = carla_interface_shared_variables

        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False
        self._data = {}

        self._vehicle_id = ''
        self._trajectory = None

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
        # vehicle_transform, vehicle_velocity = self._get_current_state()
        # TODO: calculate steering angle, throttle and brake

    def load_trajectory(self):
        """Load HCR trajectory"""
        path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
        self._trajectory = np.loadtxt(os.path.join(path_trajectory_directory, self.settings.reference_trajectory_name), ',')
        print('Loaded trajectory = ', self.settings.reference_trajectory_name)

    def _get_current_state(self):
        # a vehicle transform has the format [x, y, z, yaw, pitch, roll]
        vehicle_transform = self.carla_interface_shared_variables.agents[self._vehicle_id].transform
        vehicle_velocity = self.carla_interface_shared_variables.agents[self._vehicle_id].velocities

        return vehicle_transform, vehicle_velocity


class PIDSettings:
    def __init__(self):
        self.controller_type = NPCControllerTypes.PID

        self.kp = 0.0
        self.kd = 0.0
        self.ki = 0.0

        # Steering Range
        self.min_steer = - math.pi / 2.
        self.max_steer = math.pi / 2.

        # reference trajectory
        self.reference_trajectory_name = None

    def as_dict(self):
        return self.__dict__

    def __str__(self):
        return str('PID Controller Settings')

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class PIDSettingsDialog(QtWidgets.QDialog):
    def __init__(self, module_manager, settings, parent=None):
        super().__init__(parent=parent)
        # TODO: implement a dialog to change pid settings
