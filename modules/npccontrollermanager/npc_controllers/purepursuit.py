import os

import numpy as np
from PyQt5 import QtWidgets

from modules.carlainterface.carlainterface_sharedvariables import CarlaInterfaceSharedVariables
from modules.npccontrollermanager.npccontrollermanager_sharedvariables import NPCControllerSharedVariables
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes


class PurePursuitControllerProcess:
    """ This is a simple implementation of a pure pursuit vehicle controller. For more information on this type of controller please use Google, it is pretty common.
    This simple implementation does not use the back axle as the origin of the vehicle frame as it should, so it should not be used when high precision is required.
    """

    def __init__(self, settings, shared_variables: NPCControllerSharedVariables, carla_interface_shared_variables: CarlaInterfaceSharedVariables):
        self.settings = settings
        self.shared_variables = shared_variables
        self.carla_interface_shared_variables = carla_interface_shared_variables

        self._trajectory = None
        self._max_steering_angle = self.carla_interface_shared_variables.agents[self.settings.vehicle_id].max_steering_angle

    def get_ready(self):
        self.load_trajectory()

    def do(self):
        """
        Calculates the vehicle steering angle, throttle and brake based on the current state and desired trajectory.
        At the end of this do function, the calculated values need to be written to shared variables. From there they are automatically used by the connected vehicle.
        Variable to write:
            self.shared_variables.brake = calculated brake between (0.0 , 1.0)
            self.shared_variables.throttle = calculated throttle between (0.0 , 1.0)
            self.shared_variables.steering_angle = calculated steering between (-1.0 , 1.0)
            self.shared_variables.handbrake = False
            self.shared_variables.reverse = False
        """
        vehicle_transform, vehicle_velocity = self._get_current_state()

        if vehicle_transform.any():
            closest_way_point_index = self._find_closest_way_point(vehicle_transform)

            if np.linalg.norm(self._trajectory[closest_way_point_index, 1:3] - vehicle_transform[0:2]) > self.settings.look_ahead_distance:
                raise RuntimeError('Pure Pursuit controller to far from path, distance = ' + str(
                    np.linalg.norm(self._trajectory[closest_way_point_index, 1:3] - vehicle_transform[0:2])))

            # calculate steering angle using the look ahead distance and trajectory. Steer point is defined as the point where the two intersect.
            first_way_point_outside_look_ahead_circle = self._find_first_way_point_outside_look_ahead_circle(vehicle_transform, closest_way_point_index)
            steer_point_in_vehicle_frame = self._calculate_steer_point(vehicle_transform, first_way_point_outside_look_ahead_circle)

            steering_angle = np.arctan2(steer_point_in_vehicle_frame[1], steer_point_in_vehicle_frame[0])

            # calculate throttle with pid controller based on velocity at closest way point
            desired_velocity = self._trajectory[closest_way_point_index, 7]

            velocity_error = desired_velocity - vehicle_velocity[0]
            throttle = self.settings.kp * velocity_error

            # write calculated values to shared
            if throttle > 0.:
                self.shared_variables.throttle = throttle
            else:
                self.shared_variables.throttle = 0.

            if throttle < 0.:
                self.shared_variables.brake = -throttle
            else:
                self.shared_variables.brake = 0.

            # steering_angle in shared velocities is normalized with respect to the maximum steering angle
            self.shared_variables.steering_angle = steering_angle / self._max_steering_angle
            self.shared_variables.handbrake = False
            self.shared_variables.reverse = False

    def _find_closest_way_point(self, vehicle_transform):
        closest_way_point_index = np.argmin(np.linalg.norm(self._trajectory[:, 1:3] - vehicle_transform[0:2], axis=1))
        return closest_way_point_index

    def _find_first_way_point_outside_look_ahead_circle(self, vehicle_transform, closest_way_point_index):
        current_way_point_index = closest_way_point_index
        current_way_point = self._trajectory[current_way_point_index, 1:3]
        while np.linalg.norm(current_way_point - vehicle_transform[0:2]) < self.settings.look_ahead_distance:
            current_way_point_index += 1
            current_way_point = self._trajectory[current_way_point_index, 1:3]

        return current_way_point_index

    def _calculate_steer_point(self, vehicle_transform, first_way_point_outside_look_ahead_circle):
        # select the two waypoint that span a line that intersects with the look ahead circle and convert them to vehicle frame
        yaw = np.radians(vehicle_transform[3])
        rotation_matrix = np.array([[np.cos(yaw), -np.sin(yaw)],
                                    [np.sin(yaw), np.cos(yaw)]])

        way_point_inside = np.dot(np.linalg.inv(rotation_matrix), self._trajectory[first_way_point_outside_look_ahead_circle - 1, 1:3] - vehicle_transform[0:2])
        way_point_outside = np.dot(np.linalg.inv(rotation_matrix), self._trajectory[first_way_point_outside_look_ahead_circle, 1:3] - vehicle_transform[0:2])

        # determine the line y=c1 * x + c2 spanned by the two points

        dx = way_point_outside[0] - way_point_inside[0]
        dy = way_point_outside[1] - way_point_inside[1]

        if abs(dx) <= 1e-2:
            print('WARNING: steering point calculation in pure pursuit controller reached singular point, approximation is used instead')
            return way_point_inside + (way_point_outside - way_point_inside) / 2.

        c1 = dy / dx
        c2 = way_point_outside[1] - c1 * way_point_outside[0]

        # solve 'y=c1 * x + c2' and 'lookahead distance^2 = x^2 + y^2' to find steer point. use abc formula to find solutions for x
        a = 1 + c1 ** 2
        b = 2 * c2 * c1
        c = c2 ** 2 - self.settings.look_ahead_distance ** 2

        d = (b ** 2) - (4 * a * c)
        x1 = (-b - np.sqrt(d)) / (2 * a)
        x2 = (-b + np.sqrt(d)) / (2 * a)

        if x1 > 0.:
            x = x1
            y = c1 * x1 + c2
        elif x2 > 0.:
            x = x2
            y = c1 * x2 + c2
        else:
            raise RuntimeError('NPC controller failed to calculate steer point')

        return np.array([x, y])

    def load_trajectory(self):
        """
        Load trajectory from csv file
        format = [index, x, y, steering_wheel_angle, throttle, brake, heading, velocity]
        """

        path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
        self._trajectory = np.loadtxt(os.path.join(path_trajectory_directory, self.settings.reference_trajectory_name), delimiter=',')
        print('Loaded trajectory = ', self.settings.reference_trajectory_name)

    def _get_current_state(self):
        # a vehicle transform has the format [x, y, z, yaw, pitch, roll]
        vehicle_transform = self.carla_interface_shared_variables.agents[self.settings.vehicle_id].transform
        vehicle_velocity = self.carla_interface_shared_variables.agents[self.settings.vehicle_id].velocities_in_vehicle_frame

        return np.array(vehicle_transform), np.array(vehicle_velocity)


class PurePursuitSettings:
    def __init__(self):
        self.controller_type = NPCControllerTypes.PURE_PURSUIT

        self.look_ahead_distance = 15.0
        self.kp = 0.1

        # reference trajectory
        self.reference_trajectory_name = 'demo_map_human_trajectory.csv'

        # vehicle to control
        self.vehicle_id = ''

    def as_dict(self):
        return self.__dict__

    def __str__(self):
        return str('Pure Pursuit Controller Settings')

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class PurePursuitSettingsDialog(QtWidgets.QDialog):
    def __init__(self, module_manager, settings, parent=None):
        super().__init__(parent=parent)
        # TODO: implement a dialog to change pure pursuit settings
