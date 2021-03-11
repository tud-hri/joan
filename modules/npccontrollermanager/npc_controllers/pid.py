import math
import os
import numpy as np

from PyQt5 import QtWidgets
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes
from modules.npccontrollermanager.npccontrollermanager_sharedvariables import NPCControllerSharedVariables
from modules.carlainterface.carlainterface_sharedvariables import CarlaInterfaceSharedVariables


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
        self.index = 0

        self._vehicle_id = ''
        self._trajectory = None

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.v = 0.0



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
        vehicle_transform, vehicle_velocity = self._get_current_state()
        # TODO: calculate steering angle, throttle and brake

        index = self.load_trajectory()

        # ADDED CODE (https://gitee.com/HaiFengZhiJia/PythonRobotics/blob/master/PathTracking/pure_pursuit/pure_pursuit.py):
        #  target course

        cx = self._trajectory[1]
        cy = self._trajectory[2]
        cyaw = self._trajectory[6]

        T = 100.0  # max simulation time

        print(vehicle_transform[0,0])
        # initial state
        state = State(x=vehicle_transform[0], y=vehicle_transform[1], yaw=vehicle_transform[3], v=0.0)

        lastIndex = len(cx) - 1
        time = 0.0
        x = [state.x]
        y = [state.y]
        yaw = [state.yaw]
        v = [state.v]
        t = [0.0]
        target_ind = calc_target_index(state, cx, cy)

        while T >= time and lastIndex > target_ind:
            di, target_ind = pure_pursuit_control(state, cx, cy, target_ind)
            state = update(state, ai, di)
            state = update(state, di)

            time = time + dt

            x.append(state.x)
            y.append(state.y)
            yaw.append(state.yaw)

            t.append(time)

        # Test
        assert lastIndex >= target_ind, "Cannot goal"




    def load_trajectory(self):
        """Load HCR trajectory"""
        path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
        self._trajectory = np.loadtxt(os.path.join(path_trajectory_directory, self.settings.reference_trajectory_name), delimiter=',')
        print('Loaded trajectory = ', self.settings.reference_trajectory_name)

        self.index += 1
        index = self.index
        return index

    def _get_current_state(self):
        # a vehicle transform has the format [x, y, z, yaw, pitch, roll]
        vehicle_transform = self.carla_interface_shared_variables.agents[self._vehicle_id].transform
        vehicle_velocity = self.carla_interface_shared_variables.agents[self._vehicle_id].velocities

        return vehicle_transform, vehicle_velocity

    # ADDED CODE:
    def pure_pursuit_control(state, cx, cy, pind):

        ind = calc_target_index(state, cx, cy)

        if pind >= ind:
            ind = pind

        if ind < len(cx):
            tx = cx[ind]
            ty = cy[ind]
        else:
            tx = cx[-1]
            ty = cy[-1]
            ind = len(cx) - 1

        alpha = math.atan2(ty - state.y, tx - state.x) - state.yaw

        return ind

    def calc_target_index(state, cx, cy):

        # search nearest point index
        dx = [state.x - icx for icx in cx]
        dy = [state.y - icy for icy in cy]
        d = [abs(math.sqrt(idx ** 2 + idy ** 2)) for (idx, idy) in zip(dx, dy)]
        ind = d.index(min(d))
        L = 0.0

        Lf = k * state.v + Lfc

        # search look ahead target point index
        while Lf > L and (ind + 1) < len(cx):
            dx = cx[ind + 1] - cx[ind]
            dy = cx[ind + 1] - cx[ind]
            L += math.sqrt(dx ** 2 + dy ** 2)
            ind += 1

        return ind

# ORIGINAL CODE:
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
        self.reference_trajectory_name = 'test_trajectory_sensodrive.csv'

        # Parameters for added code:

        self.k = 0.1  # look forward gain
        self.Lfc = 1.0  # look-ahead distance
        self.Kp = 1.0  # speed propotional gain
        self.dt = 0.1  # [s]
        self.L = 2.9  # [m] wheel base of vehicle

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


class State:

    def __init__(self, x=0.0, y=0.0, yaw=0.0, v=0.0):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v