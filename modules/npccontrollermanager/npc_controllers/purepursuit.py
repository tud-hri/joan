import os
import glob
import copy
from enum import Enum

import numpy as np
from PyQt5 import QtWidgets, uic

from modules.carlainterface.carlainterface_sharedvariables import CarlaInterfaceSharedVariables
from modules.npccontrollermanager.npccontrollermanager_sharedvariables import NPCControllerSharedVariables
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes
from tools import AveragedFloat


class PurePursuitControllerProcess:
    """ This is a simple implementation of a pure pursuit vehicle controller. For more information on this type of controller please use Google, it is pretty common.
    This simple implementation does not use the back axle as the origin of the vehicle frame as it should, so it should not be used when high precision is required.
    """

    def __init__(self, settings, shared_variables: NPCControllerSharedVariables,
                 carla_interface_shared_variables: CarlaInterfaceSharedVariables):
        self.settings = settings
        self.shared_variables = shared_variables
        self.carla_interface_shared_variables = carla_interface_shared_variables

        self._trajectory = None
        self.rear_axle_position = None
        self.vehicle_velocity = None
        self.vehicle_orientation = None
        self.last_velocity_error = 0.
        self.last_control_time_stamp = 0
        self.error_rate = AveragedFloat()

        self._max_steering_angle = self.carla_interface_shared_variables.agents[
            self.settings.vehicle_id].max_steering_angle

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
        self.rear_axle_position, self.vehicle_velocity, self.vehicle_orientation, time_stamp = self._get_current_state()
        dt = (time_stamp - self.last_control_time_stamp) * 1e-9

        if self.rear_axle_position.any() and dt:
            self.last_control_time_stamp = time_stamp
            closest_way_point_index = self._find_closest_way_point(self.rear_axle_position)

            if np.linalg.norm(self._trajectory[closest_way_point_index, 1:3] - self.rear_axle_position[
                                                                               0:2]) > self.look_ahead_distance:
                raise RuntimeError('Pure Pursuit controller to far from path, distance = ' + str(
                    np.linalg.norm(self._trajectory[closest_way_point_index, 1:3] - self.rear_axle_position[0:2])))

            # calculate steering angle using the look ahead distance and trajectory. Steer point is defined as the point where the two intersect.
            first_way_point_outside_look_ahead_circle = self._find_first_way_point_outside_look_ahead_circle(
                self.rear_axle_position, closest_way_point_index)
            steer_point_in_vehicle_frame = self._calculate_steer_point(self.rear_axle_position,
                                                                       self.vehicle_orientation,
                                                                       first_way_point_outside_look_ahead_circle)

            steering_angle = np.arctan2(steer_point_in_vehicle_frame[1], steer_point_in_vehicle_frame[0])

            # calculate throttle with pid controller based on velocity at closest way point
            if self._trajectory[closest_way_point_index, 8] == -1:
                desired_velocity = self._trajectory[closest_way_point_index, 7]
            else:
                desired_velocity = self._trajectory[closest_way_point_index, 8]



            velocity_error = desired_velocity - self.vehicle_velocity[0]

            self.error_rate.value = (velocity_error - self.last_velocity_error) / dt
            self.last_velocity_error = velocity_error

            throttle = self.settings.kp * velocity_error + self.settings.kd * self.error_rate.value

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
            self.shared_variables.steering_angle = self.settings.steering_gain * steering_angle / self._max_steering_angle
            self.shared_variables.handbrake = False
            self.shared_variables.reverse = False
            self.shared_variables.desired_velocity = desired_velocity

    @property
    def look_ahead_distance(self):
        if self.settings.use_dynamic_look_ahead_distance:
            return self.settings.dynamic_lad_a * self.vehicle_velocity[0] + self.settings.dynamic_lad_b
        else:
            return self.settings.static_look_ahead_distance

    def _find_closest_way_point(self, vehicle_transform):
        closest_way_point_index = np.argmin(np.linalg.norm(self._trajectory[:, 1:3] - vehicle_transform[0:2], axis=1))
        return closest_way_point_index

    def _find_first_way_point_outside_look_ahead_circle(self, vehicle_transform, closest_way_point_index):
        current_way_point_index = closest_way_point_index
        current_way_point = self._trajectory[current_way_point_index, 1:3]
        while np.linalg.norm(current_way_point - vehicle_transform[0:2]) < self.look_ahead_distance:
            current_way_point_index += 1
            if current_way_point_index < len(self._trajectory[:, 1]):
                current_way_point = self._trajectory[current_way_point_index, 1:3]

        return current_way_point_index

    def _calculate_steer_point(self, rear_axle_position, vehicle_orientation,
                               first_way_point_outside_look_ahead_circle):
        # select the two waypoint that span a line that intersects with the look ahead circle and convert them to vehicle frame
        yaw = np.radians(vehicle_orientation[0])
        rotation_matrix = np.array([[np.cos(yaw), -np.sin(yaw)],
                                    [np.sin(yaw), np.cos(yaw)]])

        way_point_inside = np.dot(np.linalg.inv(rotation_matrix),
                                  self._trajectory[first_way_point_outside_look_ahead_circle - 1,
                                  1:3] - rear_axle_position[0:2])
        way_point_outside = np.dot(np.linalg.inv(rotation_matrix),
                                   self._trajectory[first_way_point_outside_look_ahead_circle,
                                   1:3] - rear_axle_position[0:2])

        # determine the line y=c1 * x + c2 spanned by the two points

        dx = way_point_outside[0] - way_point_inside[0]
        dy = way_point_outside[1] - way_point_inside[1]

        if abs(dx) <= 1e-2:
            print(
                'WARNING: steering point calculation in pure pursuit controller reached singular point, approximation is used instead')
            return way_point_inside + (way_point_outside - way_point_inside) / 2.

        c1 = dy / dx
        c2 = way_point_outside[1] - c1 * way_point_outside[0]

        # solve 'y=c1 * x + c2' and 'lookahead distance^2 = x^2 + y^2' to find steer point. use abc formula to find solutions for x
        a = 1 + c1 ** 2
        b = 2 * c2 * c1
        c = c2 ** 2 - self.look_ahead_distance ** 2

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

        path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../trajectories')
        self._trajectory = np.loadtxt(os.path.join(path_trajectory_directory, self.settings.reference_trajectory_name),
                                      delimiter=',')
        print('Loaded trajectory = ', self.settings.reference_trajectory_name)

    def _get_current_state(self):
        rear_axle_position = self.carla_interface_shared_variables.agents[self.settings.vehicle_id].rear_axle_position
        vehicle_velocity = self.carla_interface_shared_variables.agents[
            self.settings.vehicle_id].velocities_in_vehicle_frame
        vehicle_orientation = self.carla_interface_shared_variables.agents[self.settings.vehicle_id].transform[3:6]
        time_stamp = self.carla_interface_shared_variables.time

        return np.array(rear_axle_position), np.array(vehicle_velocity), np.array(vehicle_orientation), time_stamp


class PurePursuitSettings:
    def __init__(self):
        self.controller_type = NPCControllerTypes.PURE_PURSUIT

        self.kp = 150
        self.kd = 10

        self.use_dynamic_look_ahead_distance = True
        self.static_look_ahead_distance = 15.0
        self.steering_gain = 4.

        # a dynamic look ahead distance is calculated as LAD = a * v + b where v is velocity
        self.dynamic_lad_a = 0.5
        self.dynamic_lad_b = 8.0

        # reference trajectory
        self.reference_trajectory_name = 'demo_map_human_trajectory.csv'

        # vehicle to control
        self.vehicle_id = ''

    def as_dict(self):
        return_dict = copy.copy(self.__dict__)
        for key, item in self.__dict__.items():
            if isinstance(item, Enum):
                return_dict[key] = item.value
        return return_dict

    def __str__(self):
        return str('Pure Pursuit Controller Settings')

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            if key == 'controller_type':
                self.__setattr__(key, NPCControllerTypes(value))
            else:
                self.__setattr__(key, value)


class PurePursuitSettingsDialog(QtWidgets.QDialog):
    def __init__(self, module_manager, settings: PurePursuitSettings, parent=None):
        super().__init__(parent=parent)
        self.module_manager = module_manager
        self.pure_pursuit_settings = settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/pure_pursuit_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self.dynamicLADCheckBox.stateChanged.connect(self._update_static_dynamic_look_ahead_distance)
        self._fill_trajectory_combobox()
        self.display_values()

        self.show()

    def accept(self):
        self.pure_pursuit_settings.reference_trajectory_name = self.trajectoryComboBox.currentText()
        self.pure_pursuit_settings.static_look_ahead_distance = self.staticLADDoubleSpinBox.value()
        self.pure_pursuit_settings.use_dynamic_look_ahead_distance = self.dynamicLADCheckBox.isChecked()
        self.pure_pursuit_settings.steering_gain = self.steeringGainDoubleSpinBox.value()
        self.pure_pursuit_settings.dynamic_lad_a = self.aDoubleSpinBox.value()
        self.pure_pursuit_settings.dynamic_lad_b = self.bDoubleSpinBox.value()
        self.pure_pursuit_settings.kp = self.kpDoubleSpinBox.value()
        self.pure_pursuit_settings.kd = self.kdDoubleSpinBox.value()

        super().accept()

    def display_values(self, settings=None):
        if not settings:
            settings = self.pure_pursuit_settings

        self.trajectoryComboBox.setCurrentIndex(self.trajectoryComboBox.findText(settings.reference_trajectory_name))
        self.staticLADDoubleSpinBox.setValue(settings.static_look_ahead_distance)
        self.dynamicLADCheckBox.setChecked(settings.use_dynamic_look_ahead_distance)
        self.steeringGainDoubleSpinBox.setValue(settings.steering_gain)
        self.aDoubleSpinBox.setValue(settings.dynamic_lad_a)
        self.bDoubleSpinBox.setValue(settings.dynamic_lad_b)
        self.kpDoubleSpinBox.setValue(settings.kp)
        self.kdDoubleSpinBox.setValue(settings.kd)

    def _update_static_dynamic_look_ahead_distance(self):
        use_dynamic = self.dynamicLADCheckBox.isChecked()

        self.staticLADLabel.setEnabled(not use_dynamic)
        self.staticLADDoubleSpinBox.setEnabled(not use_dynamic)
        self.LADExplanationLabel.setEnabled(use_dynamic)
        self.aLabel.setEnabled(use_dynamic)
        self.bLabel.setEnabled(use_dynamic)
        self.aDoubleSpinBox.setEnabled(use_dynamic)
        self.bDoubleSpinBox.setEnabled(use_dynamic)

    def _set_default_values(self):
        self.display_values(NPCControllerTypes.PURE_PURSUIT.settings())

    def _fill_trajectory_combobox(self):
        self.trajectoryComboBox.addItem(' ')

        path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
        file_names = glob.glob(os.path.join(path_trajectory_directory, '*.csv'))
        for file in file_names:
            self.trajectoryComboBox.addItem(os.path.basename(file))
