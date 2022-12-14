import random, os, math
import numpy as np

import carla
from trajectories.trajectories import Track

from PyQt5 import uic, QtWidgets
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from modules.joanmodules import JOANModules
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox


class EgoVehicleSettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings, module_manager, parent=None):
        super().__init__(parent)

        self.settings = settings
        self.module_manager = module_manager
        self.carla_interface_overall_settings = self.module_manager.module_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/ego_vehicle_settings_ui.ui"), self)
        self.msg_box = QMessageBox()
        self.msg_box.setTextFormat(QtCore.Qt.RichText)

        self.button_box_egovehicle_settings.button(self.button_box_egovehicle_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)
        self.btn_update.clicked.connect(lambda: self.update_settings(self.settings))
        self.customSpawnpointCheckBox.stateChanged.connect(self.update_spinbox_enabled)
        self.display_values()

        self.update_settings(self.settings)

    def show(self):
        self.update_settings(self.settings)
        super().show()

    def update_spinbox_enabled(self):
        for spinbox in [self.spawnpointXSpinBox, self.spawnpointYSpinBox, self.spawnpointZSpinBox, self.spawnpointYawSpinBox]:
            spinbox.setEnabled(self.customSpawnpointCheckBox.isChecked())

    def update_parameters(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.steering_ratio = self.spin_steering_ratio.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_haptic_controllers.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()

        self.settings.use_custom_spawn_point = self.customSpawnpointCheckBox.isChecked()
        self.settings.custom_spawn_point_location[0] = self.spawnpointXSpinBox.value()
        self.settings.custom_spawn_point_location[1] = self.spawnpointYSpinBox.value()
        self.settings.custom_spawn_point_location[2] = self.spawnpointZSpinBox.value()
        self.settings.custom_spawn_point_rotation = self.spawnpointYawSpinBox.value()

        for settings in self.carla_interface_overall_settings.agents.values():
            if settings.identifier != self.settings.identifier:  # exlude own settings
                if settings.selected_spawnpoint == self.combo_spawnpoints.currentText() and settings.selected_spawnpoint != 'None':
                    self.msg_box.setText('This spawnpoint was already chosen for another agent \n'
                                         'resetting spawnpoint to None')
                    self.msg_box.exec()
                    self.settings.selected_spawnpoint = 'None'
                    break
                else:
                    self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()

        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        self.display_values()

    def accept(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.steering_ratio = self.spin_steering_ratio.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_haptic_controllers.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()

        self.settings.use_custom_spawn_point = self.customSpawnpointCheckBox.isChecked()
        self.settings.custom_spawn_point_location[0] = self.spawnpointXSpinBox.value()
        self.settings.custom_spawn_point_location[1] = self.spawnpointYSpinBox.value()
        self.settings.custom_spawn_point_location[2] = self.spawnpointZSpinBox.value()
        self.settings.custom_spawn_point_rotation = self.spawnpointYawSpinBox.value()

        for settings in self.carla_interface_overall_settings.agents.values():
            if settings.identifier != self.settings.identifier:  # exlude own settings
                if settings.selected_spawnpoint == self.combo_spawnpoints.currentText() and settings.selected_spawnpoint != 'None':
                    self.msg_box.setText('This spawnpoint was already chosen for another agent \n'
                                         'resetting spawnpoint to None')
                    self.msg_box.exec()
                    self.settings.selected_spawnpoint = 'None'
                    break
            else:
                self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        super().accept()

    def display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.settings

        self.customSpawnpointCheckBox.setChecked(settings_to_display.use_custom_spawn_point)
        self.spawnpointXSpinBox.setValue(settings_to_display.custom_spawn_point_location[0])
        self.spawnpointYSpinBox.setValue(settings_to_display.custom_spawn_point_location[1])
        self.spawnpointZSpinBox.setValue(settings_to_display.custom_spawn_point_location[2])
        self.spawnpointYawSpinBox.setValue(settings_to_display.custom_spawn_point_rotation)

        idx_controller = self.combo_haptic_controllers.findText(settings_to_display.selected_controller)
        self.combo_haptic_controllers.setCurrentIndex(idx_controller)

        idx_input = self.combo_input.findText(settings_to_display.selected_input)
        self.combo_input.setCurrentIndex(idx_input)

        idx_car = self.combo_car_type.findText(settings_to_display.selected_car)
        self.combo_car_type.setCurrentIndex(idx_car)

        self.combo_spawnpoints.setCurrentText(settings_to_display.selected_spawnpoint)

        self.spin_velocity.setValue(settings_to_display.velocity)
        self.spin_steering_ratio.setValue(settings_to_display.steering_ratio)
        self.check_box_set_vel.setChecked(settings_to_display.set_velocity)
        self.update_spinbox_enabled()

    def _set_default_values(self):
        self.display_values(AgentTypes.EGO_VEHICLE.settings())

    def update_settings(self, settings):
        try:
            # Update hardware inputs according to current settings:
            self.combo_input.clear()
            self.combo_input.addItem('None')
            HardwareManagerSettings = self.module_manager.central_settings.get_settings(JOANModules.HARDWARE_MANAGER)
            for inputs in HardwareManagerSettings.inputs.values():
                self.combo_input.addItem(str(inputs))
            idx = self.combo_input.findText(
                settings.selected_input)
            if idx != -1:
                self.combo_input.setCurrentIndex(idx)

            # update available vehicles
            self.combo_car_type.clear()
            self.combo_car_type.addItem('None')
            self.combo_car_type.addItems(self.module_manager.vehicle_tags)
            idx = self.combo_car_type.findText(settings.selected_car)
            if idx != -1:
                self.combo_car_type.setCurrentIndex(idx)

            # update available spawn_points:
            self.combo_spawnpoints.clear()
            self.combo_spawnpoints.addItem('None')
            self.combo_spawnpoints.addItems(self.module_manager.spawn_points)
            idx = self.combo_spawnpoints.findText(
                settings.selected_spawnpoint)
            if idx != -1:
                self.combo_spawnpoints.setCurrentIndex(idx)

            # update available controllers according to current settings:
            self.combo_haptic_controllers.clear()
            self.combo_haptic_controllers.addItem('None')
            HapticControllerManagerSettings = self.module_manager.central_settings.get_settings(JOANModules.HAPTIC_CONTROLLER_MANAGER)
            for haptic_controller in HapticControllerManagerSettings.haptic_controllers.values():
                self.combo_haptic_controllers.addItem(str(haptic_controller))
            idx = self.combo_haptic_controllers.findText(
                settings.selected_controller)
            if idx != -1:
                self.combo_haptic_controllers.setCurrentIndex(idx)
        except AttributeError:
            # Catching attribute error when using default car settings
            pass


class EgoVehicleProcess:
    def __init__(self, carla_mp, settings, shared_variables):
        self.settings = settings
        self.shared_variables = shared_variables
        self.carlainterface_mp = carla_mp

        self._control = carla.VehicleControl()
        if self.settings.selected_car != 'None':
            self._BP = random.choice(self.carlainterface_mp.vehicle_blueprint_library.filter("vehicle." + self.settings.selected_car))
        self._control = carla.VehicleControl()
        self.world_map = self.carlainterface_mp.world.get_map()
        self.map_name = self.world_map.name.split('/')[-1]
        self.trajectory_object = Track(self.map_name)

        torque_curve = []
        gears = []

        torque_curve.append(carla.Vector2D(x=0, y=600))
        torque_curve.append(carla.Vector2D(x=14000, y=600))
        gears.append(carla.GearPhysicsControl(ratio=7.73, down_ratio=0.0, up_ratio=100.))

        if self.settings.selected_spawnpoint != 'None' or self.settings.use_custom_spawn_point:
            if self.settings.selected_car != 'None':
                if self.settings.use_custom_spawn_point:
                    spawn_transform = carla.Transform(location=carla.Location(*self.settings.custom_spawn_point_location),
                                                      rotation=carla.Rotation(yaw=self.settings.custom_spawn_point_rotation))
                else:
                    spawn_transform = self.carlainterface_mp.spawn_point_objects[self.carlainterface_mp.spawn_points.index(self.settings.selected_spawnpoint)]
                self.spawned_vehicle = self.carlainterface_mp.world.spawn_actor(self._BP, spawn_transform)
                physics = self.spawned_vehicle.get_physics_control()
                physics.torque_curve = torque_curve
                physics.max_rpm = 14000
                physics.moi = 1.5
                physics.damping_rate_full_throttle = 0.35
                physics.damping_rate_zero_throttle_clutch_engaged = 0.35  # simulate that the clutch is always disengaged with no throttle
                physics.damping_rate_zero_throttle_clutch_disengaged = 0.35
                physics.clutch_strength = 1000
                physics.final_ratio = 1  # ratio from transmission to wheels
                physics.forward_gears = gears
                physics.mass = 1475  # kg (Audi S3)
                physics.drag_coefficient = 0.24
                physics.gear_switch_time = 0.0
                physics.use_gear_autobox = False
                self.spawned_vehicle.apply_physics_control(physics)
                self.max_steering_angle = physics.wheels[0].max_steer_angle

    def do(self):
        if self.settings.selected_input != 'None' and hasattr(self, 'spawned_vehicle'):
            max_angle_car = math.radians(self.max_steering_angle)
            max_angle_steering_wheel = max_angle_car * self.settings.steering_ratio
            self._control.steer = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].steering_angle / max_angle_steering_wheel
            self._control.reverse = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].reverse
            self._control.hand_brake = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].handbrake
            self._control.brake = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].brake
            if self.settings.set_velocity:
                self._control.brake, self._control.throttle = self.apply_cruise_control()
            else:
                self._control.throttle = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].throttle

            self.spawned_vehicle.apply_control(self._control)
            try:
                self.calculate_plotter_road_arrays()
            except IndexError:
                pass

        self.set_shared_variables()

    def apply_cruise_control(self):
        velocity = math.sqrt(self.spawned_vehicle.get_velocity().x ** 2 + self.spawned_vehicle.get_velocity().y ** 2)
        acceleration = math.sqrt(self.spawned_vehicle.get_acceleration().x ** 2 + self.spawned_vehicle.get_acceleration().y ** 2)
        vel_error = self.settings.velocity / 3.6 - velocity
        vel_error_rate = acceleration
        kp = 150
        kd = 10
        temp = kp * vel_error + kd * vel_error_rate
        if temp > 100:
            temp = 100
        output = temp / 100

        if output < 0:
            brake = -output
            throttle = 0
        elif output > 0:
            brake = 0
            throttle = output
        else:
            throttle = 0
            brake = 0

        return brake, throttle

    def destroy(self):
        if hasattr(self, 'spawned_vehicle') and self.spawned_vehicle.is_alive:
            self.spawned_vehicle.destroy()

    def calculate_plotter_road_arrays(self):
        data_road_x = []
        data_road_x_inner = []
        data_road_x_outer = []
        data_road_y = []
        data_road_y_inner = []
        data_road_y_outer = []
        data_road_psi = []
        data_road_lanewidth = []

        if self.spawned_vehicle is not None:
            vehicle_location = self.spawned_vehicle.get_location()
            closest_waypoint = self.world_map.get_waypoint(vehicle_location, project_to_road=True)

            # previous points
            previous_waypoints = []
            for a in reversed(range(1, 26)):
                previous_waypoints.append(closest_waypoint.previous(a))

            # next
            next_waypoints = []
            for a in range(1, 26):
                next_waypoints.append(closest_waypoint.next(a))

            for waypoints in previous_waypoints:
                data_road_x.append(waypoints[0].transform.location.x)
                data_road_y.append(waypoints[0].transform.location.y)
                data_road_lanewidth.append(waypoints[0].lane_width)

            for waypoints in next_waypoints:
                data_road_x.append(waypoints[0].transform.location.x)
                data_road_y.append(waypoints[0].transform.location.y)
                data_road_lanewidth.append(waypoints[0].lane_width)

            pos_array = np.array([[data_road_x], [data_road_y]])
            diff = np.transpose(np.diff(pos_array))

            x_unit_vector = np.array([[1], [0]])
            for row in diff:
                data_road_psi.append(self.compute_angle(row.ravel(), x_unit_vector.ravel()))

            data_road_psi.append(0)

            iter_x = 0
            for roadpoint_x in data_road_x:
                data_road_x_outer.append(roadpoint_x - math.sin(data_road_psi[iter_x]) * data_road_lanewidth[iter_x] / 2)
                data_road_x_inner.append(roadpoint_x + math.sin(data_road_psi[iter_x]) * data_road_lanewidth[iter_x] / 2)
                iter_x = iter_x + 1

            iter_y = 0
            for roadpoint_y in data_road_y:
                data_road_y_outer.append(roadpoint_y - math.cos(data_road_psi[iter_y]) * data_road_lanewidth[iter_y] / 2)
                data_road_y_inner.append(roadpoint_y + math.cos(data_road_psi[iter_y]) * data_road_lanewidth[iter_y] / 2)
                iter_y = iter_y + 1

            # set shared road variables:
            self.shared_variables.data_road_x = data_road_x
            self.shared_variables.data_road_x_inner = data_road_x_inner
            self.shared_variables.data_road_x_outer = data_road_x_outer
            self.shared_variables.data_road_y = data_road_y
            self.shared_variables.data_road_y_inner = data_road_y_inner
            self.shared_variables.data_road_y_outer = data_road_y_outer
            self.shared_variables.data_road_psi = data_road_psi
            self.shared_variables.data_road_lanewidth = data_road_lanewidth

    def compute_angle(self, v1, v2):
        arg1 = np.cross(v1, v2)
        arg2 = np.dot(v1, v2)
        angle = np.arctan2(arg1, arg2)
        return angle

    def set_shared_variables(self):
        if hasattr(self, 'spawned_vehicle'):
            actor_snap_shot = self.carlainterface_mp.world.get_snapshot().find(self.spawned_vehicle.id)

            rotation = actor_snap_shot.get_transform().rotation
            center_location = actor_snap_shot.get_transform().location
            self.shared_variables.transform = [center_location.x,
                                               center_location.y,
                                               center_location.z,
                                               rotation.yaw,
                                               rotation.pitch,
                                               rotation.roll]
            linear_velocity = actor_snap_shot.get_velocity()
            self.shared_variables.velocities_in_world_frame = [linear_velocity.x,
                                                               linear_velocity.y,
                                                               linear_velocity.z,
                                                               actor_snap_shot.get_angular_velocity().x,
                                                               actor_snap_shot.get_angular_velocity().y,
                                                               actor_snap_shot.get_angular_velocity().z]

            rotation_matrix = self.get_rotation_matrix_from_carla(rotation.roll, rotation.pitch, rotation.yaw)
            velocities_in_vehicle_frame = np.linalg.inv(rotation_matrix) @ np.array([linear_velocity.x, linear_velocity.y, linear_velocity.z])
            self.shared_variables.velocities_in_vehicle_frame = velocities_in_vehicle_frame

            self.shared_variables.accelerations_in_world_frame = [actor_snap_shot.get_acceleration().x,
                                                                  actor_snap_shot.get_acceleration().y,
                                                                  actor_snap_shot.get_acceleration().z]

            accelerations = actor_snap_shot.get_acceleration()
            self.shared_variables.accelerations_in_world_frame = [accelerations.x,
                                                                  accelerations.y,
                                                                  accelerations.z]

            accelerations_in_vehicle_frame = np.linalg.inv(rotation_matrix) @ np.array([accelerations.x, accelerations.y, accelerations.z])
            self.shared_variables.accelerations_in_vehicle_frame = accelerations_in_vehicle_frame

            latest_applied_control = self.spawned_vehicle.get_control()
            self.shared_variables.applied_input = [float(latest_applied_control.steer),
                                                   float(latest_applied_control.reverse),
                                                   float(latest_applied_control.hand_brake),
                                                   float(latest_applied_control.brake),
                                                   float(latest_applied_control.throttle)]
            if self.settings.set_velocity:
                self.shared_variables.cruise_control_speed = self.settings.velocity / 3.6
            else:
                self.shared_variables.cruise_control_speed = -1  # Set to -1 when no cruise control is applied

    @staticmethod
    def get_rotation_matrix_from_carla(roll, pitch, yaw, degrees=True):
        """ calculation based on this github issue: https://github.com/carla-simulator/carla/issues/58 because carla uses some rather unconventional conventions."""
        if degrees:
            roll, pitch, yaw = np.radians([roll, pitch, yaw])

        yaw_matrix = np.array([
            [math.cos(yaw), -math.sin(yaw), 0],
            [math.sin(yaw), math.cos(yaw), 0],
            [0, 0, 1]
        ])

        pitch_matrix = np.array([
            [math.cos(pitch), 0, -math.sin(pitch)],
            [0, 1, 0],
            [math.sin(pitch), 0, math.cos(pitch)]
        ])

        roll_matrix = np.array([
            [1, 0, 0],
            [0, math.cos(roll), math.sin(roll)],
            [0, -math.sin(roll), math.cos(roll)]
        ])

        rotation_matrix = yaw_matrix @ pitch_matrix @ roll_matrix
        return rotation_matrix

class EgoVehicleSettings:
    """
    Class containing the default settings for an egovehicle
    """

    def __init__(self, identifier=''):
        """
        Initializes the class with default variables
        """
        self.selected_input = 'None'
        self.selected_controller = 'None'
        self.selected_spawnpoint = 'Spawnpoint 0'
        self.selected_car = 'audi.hapticslab'
        self.velocity = 50
        self.set_velocity = False
        self.identifier = identifier
        self.steering_ratio = 13
        self.agent_type = AgentTypes.EGO_VEHICLE.value

        self.use_custom_spawn_point = False
        self.custom_spawn_point_location = [0.0, 0.0, 0.0]
        self.custom_spawn_point_rotation = 0.0

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

    def __str__(self):
        return self.identifier
