import random, os, sys, glob, math
import numpy as np

sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
    sys.version_info.major,
    sys.version_info.minor,
    'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
import carla

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
        self.display_values()

        self.update_settings(self.settings)

    def show(self):
        self.update_settings(self.settings)
        super().show()

    def update_parameters(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_haptic_controllers.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
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
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_haptic_controllers.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
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

        idx_controller = self.combo_haptic_controllers.findText(settings_to_display.selected_controller)
        self.combo_haptic_controllers.setCurrentIndex(idx_controller)

        idx_input = self.combo_input.findText(settings_to_display.selected_input)
        self.combo_input.setCurrentIndex(idx_input)

        idx_car = self.combo_car_type.findText(settings_to_display.selected_car)
        self.combo_car_type.setCurrentIndex(idx_car)

        self.combo_spawnpoints.setCurrentText(settings_to_display.selected_spawnpoint)

        self.spin_velocity.setValue(settings_to_display.velocity)
        self.check_box_set_vel.setChecked(settings_to_display.set_velocity)

    def _set_default_values(self):
        self.display_values(AgentTypes.EGO_VEHICLE.settings())

    def update_settings(self, settings):
        try:
            # Update hardware inputs according to current settings:
            self.combo_input.clear()
            self.combo_input.addItem('None')
            HardwareManagerSettings = self.module_manager.singleton_settings.get_settings(JOANModules.HARDWARE_MANAGER)
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
            HapticControllerManagerSettings = self.module_manager.singleton_settings.get_settings(JOANModules.HAPTIC_CONTROLLER_MANAGER)
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
        self._BP = random.choice(self.carlainterface_mp.vehicle_blueprint_library.filter("vehicle." + self.settings.selected_car))
        self._control = carla.VehicleControl()
        self.world_map = self.carlainterface_mp.world.get_map()
        torque_curve = []
        gears = []

        torque_curve.append(carla.Vector2D(x=0, y=600))
        torque_curve.append(carla.Vector2D(x=14000, y=600))
        gears.append(carla.GearPhysicsControl(ratio=7.73, down_ratio=0.5, up_ratio=1))

        if self.settings.selected_spawnpoint != 'None':
            self.spawned_vehicle = self.carlainterface_mp.world.spawn_actor(self._BP, self.carlainterface_mp.spawn_point_objects[
                self.carlainterface_mp.spawn_points.index(self.settings.selected_spawnpoint)])
            physics = self.spawned_vehicle.get_physics_control()
            physics.torque_curve = torque_curve
            physics.max_rpm = 14000
            physics.moi = 1.5
            physics.final_ratio = 1
            physics.clutch_strength = 1000  # very big no clutch
            physics.final_ratio = 1  # ratio from transmission to wheels
            physics.forward_gears = gears
            physics.mass = 2316
            physics.drag_coefficient = 0.24
            physics.gear_switch_time = 0
            self.spawned_vehicle.apply_physics_control(physics)

    def do(self):
        if self.settings.selected_input != 'None' and hasattr(self, 'spawned_vehicle'):
            self._control.steer = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].steering_angle / math.radians(450)
            self._control.reverse = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].reverse
            self._control.hand_brake = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].handbrake
            self._control.brake = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].brake
            if self.settings.set_velocity:
                vel_error = self.settings.velocity - (math.sqrt(
                    self.spawned_vehicle.get_velocity().x ** 2 + self.spawned_vehicle.get_velocity().y ** 2 + self.spawned_vehicle.get_velocity().z ** 2) * 3.6)
                vel_error_rate = (math.sqrt(
                    self.spawned_vehicle.get_acceleration().x ** 2 + self.spawned_vehicle.get_acceleration().y ** 2 + self.spawned_vehicle.get_acceleration().z ** 2) * 3.6)
                error_velocity = [vel_error, vel_error_rate]

                pd_vel_output = self.velocity_PD_controller(error_velocity)
                if pd_vel_output < 0:
                    self._control.brake = -pd_vel_output
                    self._control.throttle = 0
                    if pd_vel_output < -1:
                        self._control.brake = 1
                elif pd_vel_output > 0:
                    if self._control.brake == 0:
                        self._control.throttle = pd_vel_output
                    else:
                        self._control.throttle = 0
            else:
                self._control.throttle = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].throttle

            self.spawned_vehicle.apply_control(self._control)
            self.calculate_plotter_road_arrays()

        self.set_shared_variables()

    def destroy(self):
        if hasattr(self, 'spawned_vehicle'):
            self.spawned_vehicle.destroy()

    def velocity_PD_controller(self, vel_error):
        _kp_vel = 50
        _kd_vel = 1
        temp = _kp_vel * vel_error[0] + _kd_vel * vel_error[1]

        if temp > 100:
            temp = 100

        output = temp / 100

        return output

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
            self.shared_variables.transform = [self.spawned_vehicle.get_transform().location.x,
                                               self.spawned_vehicle.get_transform().location.y,
                                               self.spawned_vehicle.get_transform().location.z,
                                               self.spawned_vehicle.get_transform().rotation.yaw,
                                               self.spawned_vehicle.get_transform().rotation.pitch,
                                               self.spawned_vehicle.get_transform().rotation.roll]
            self.shared_variables.velocities = [self.spawned_vehicle.get_velocity().x,
                                                self.spawned_vehicle.get_velocity().y,
                                                self.spawned_vehicle.get_velocity().z,
                                                self.spawned_vehicle.get_angular_velocity().x,
                                                self.spawned_vehicle.get_angular_velocity().y,
                                                self.spawned_vehicle.get_angular_velocity().z]
            self.shared_variables.accelerations = [self.spawned_vehicle.get_acceleration().x,
                                                   self.spawned_vehicle.get_acceleration().y,
                                                   self.spawned_vehicle.get_acceleration().z]
            latest_applied_control = self.spawned_vehicle.get_control()
            self.shared_variables.applied_input = [float(latest_applied_control.steer),
                                                   float(latest_applied_control.reverse),
                                                   float(latest_applied_control.hand_brake),
                                                   float(latest_applied_control.brake),
                                                   float(latest_applied_control.throttle)]


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
        self.selected_car = 'hapticslab.audi'
        self.velocity = 80
        self.set_velocity = False
        self.identifier = identifier

        self.agent_type = AgentTypes.EGO_VEHICLE.value

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

    def __str__(self):
        return self.identifier
