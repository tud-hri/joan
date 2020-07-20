from modules.joanmodules import JOANModules

import math
import numpy as np


class TrajectoryRecorder:
    def __init__(self, data_recorder_action, waypoint_distance):
        self._traveled_distance = 0
        self._overall_distance = 0
        self.data_recorder_action = data_recorder_action
        self.waypoint_distance = waypoint_distance

        self.should_record_trajectory = False

    def discard_current_trajectory(self):
        self._trajectory_data = None
        self._trajectory_data_spaced = None

    def make_trajectory_array(self, waypoint_distance):

        temp_diff = self._trajectory_data[-1] - self._trajectory_data[-2]

        position_difference = temp_diff[0:2]
        small_distance = np.linalg.norm(position_difference)
        self._overall_distance = self._overall_distance + small_distance
        self._traveled_distance = self._traveled_distance + small_distance

        if (self._overall_distance >= waypoint_distance):
            self._trajectory_data_spaced = np.append(self._trajectory_data_spaced, [self._trajectory_data[-1]], axis=0)
            self._overall_distance = self._overall_distance - waypoint_distance

    def trajectory_record_boolean(self, trajectory_boolean):
        self.should_record_trajectory = trajectory_boolean

    def generate_trajectory(self):
        # Add index nr to the trajectory
        indices = np.arange(len(self._trajectory_data_spaced))
        self._trajectory_data_spaced = np.insert(self._trajectory_data_spaced, 0, indices, axis=1)
        return self._trajectory_data_spaced

    def write_trajectory(self):
        _data = self.data_recorder_action.read_news(JOANModules.AGENT_MANAGER)
        car = _data['agents']['Car 1']['vehicle_object'].spawned_vehicle
        control = car.get_control()

        x_pos = car.get_transform().location.x
        y_pos = car.get_transform().location.y
        steering_wheel_angle = control.steer
        throttle_input = control.throttle
        brake_input = control.brake
        heading = car.get_transform().rotation.yaw
        vel = math.sqrt(car.get_velocity().x ** 2 + car.get_velocity().y ** 2 + car.get_velocity().z ** 2)

        self._trajectory_data = np.append(self._trajectory_data, [
            [x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading, vel]], axis=0)

        self.make_trajectory_array(self.waypoint_distance)

    def initialize_trajectory_recorder_variables(self):
        try:
            _data = self.data_recorder_action.read_news(JOANModules.AGENT_MANAGER)
            car = _data['agents']['Car 1']['vehicle_object'].spawned_vehicle
            control = car.get_control()

            x_pos = car.get_transform().location.x
            y_pos = car.get_transform().location.y
            steering_wheel_angle = control.steer
            throttle_input = control.throttle
            brake_input = control.brake
            heading = car.get_transform().rotation.yaw
            vel = math.sqrt(car.get_velocity().x ** 2 + car.get_velocity().y ** 2 + car.get_velocity().z ** 2)

            # initialize variables here because we want the current position as first entry!
            self._trajectory_data = [[x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading, vel]]
            self._trajectory_data_spaced = [
                [x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading, vel]]
        except Exception as inst:
            print(inst)
