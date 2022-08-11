import math
import os

import numpy as np
import pandas as pd
import scipy as cp
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt

from core.statesenum import State
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes
from tools import LowPassFilterBiquad
from tools.haptic_controller_tools import find_closest_node


class FDCAControllerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings, module_manager, parent=None):
        super().__init__(parent)

        self.fdca_controller_settings = settings
        self.module_manager = module_manager

        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/fdca_settings_ui.ui"), self)
        self._path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')

        self.btnbox_fdca_controller_settings.button(
            self.btnbox_fdca_controller_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)

        self.module_manager.state_machine.add_state_change_listener(self.handle_state_change)

        self.update_trajectory_list()
        self._display_values()

        self.handle_state_change()

    def handle_state_change(self):
        # disable changing of trajectory while running (would be quite dangerous)
        if self.module_manager.state_machine.current_state == State.RUNNING:
            self.cmbbox_hcr_selection.setEnabled(False)
            self.cmbbox_hcr_selection.blockSignals(True)
        else:
            self.cmbbox_hcr_selection.setEnabled(True)
            self.cmbbox_hcr_selection.blockSignals(False)

    def update_parameters(self):
        # self.slider_loha.setValue(self.spin_loha.value())
        self.fdca_controller_settings.loha = float(self.edit_loha.text())
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        try:
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_y = self.fdca_controller_settings.k_y
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_psi = self.fdca_controller_settings.k_psi
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].lohs = self.fdca_controller_settings.lohs
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].sohf = self.fdca_controller_settings.sohf
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].loha = self.fdca_controller_settings.loha
        except:
            pass

        self._display_values()

    def accept(self):
        # self.slider_loha.setValue(self.spin_loha.value())
        self.fdca_controller_settings.loha = float(self.edit_loha.text())
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.loha = float(self.edit_loha.text())
        self.fdca_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        try:
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_y = self.fdca_controller_settings.k_y
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_psi = self.fdca_controller_settings.k_psi
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].lohs = self.fdca_controller_settings.lohs
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].sohf = self.fdca_controller_settings.sohf
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].loha = self.fdca_controller_settings.loha
        except:
            pass

        super().accept()

    def _display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.fdca_controller_settings

        # update the current controller settings
        self.lbl_k_y.setText(str(settings_to_display.k_y))
        self.lbl_k_psi.setText(str(settings_to_display.k_psi))
        self.lbl_k_psi_deg.setText(str(round(math.radians(settings_to_display.k_psi), 3)))
        self.lbl_lohs.setText(str(settings_to_display.lohs))
        self.lbl_sohf.setText(str(settings_to_display.sohf))
        self.lbl_loha.setText(str(settings_to_display.loha))
        self.lbl_loha_deg.setText(str(round(math.radians(settings_to_display.loha), 3)))

        self.edit_k_y.setText(str(settings_to_display.k_y))
        self.edit_k_psi.setText(str(settings_to_display.k_psi))
        self.edit_lohs.setText(str(settings_to_display.lohs))
        self.edit_sohf.setText(str(settings_to_display.sohf))
        self.edit_loha.setText(str(settings_to_display.loha))
        # self.slider_loha.setValue(settings_to_display.loha)
        # self.spin_loha.setValue(settings_to_display.loha)

        idx_traj = self.cmbbox_hcr_selection.findText(settings_to_display.trajectory_name)
        self.cmbbox_hcr_selection.setCurrentIndex(idx_traj)

    def _set_default_values(self):
        self._display_values(HapticControllerTypes.FDCA.settings())
        self.update_parameters()

    def update_trajectory_list(self):
        """
        Check what trajectory files are present and update the selection list
        """
        # get list of csv files in directory
        if not os.path.isdir(self._path_trajectory_directory):
            os.mkdir(self._path_trajectory_directory)

        files = [filename for filename in os.listdir(self._path_trajectory_directory) if filename.endswith('csv')]

        self.cmbbox_hcr_selection.clear()
        self.cmbbox_hcr_selection.addItem('None')
        self.cmbbox_hcr_selection.addItems(files)

        idx = self.cmbbox_hcr_selection.findText(self.fdca_controller_settings.trajectory_name)
        if idx != -1:
            self.cmbbox_hcr_selection.setCurrentIndex(idx)


class FDCAControllerProcess:
    def __init__(self, settings, shared_variables, carla_interface_settings):
        self.settings = settings
        self.carla_interface_settings = carla_interface_settings
        self.shared_variables = shared_variables
        self._trajectory = None
        self.t_lookahead = 0.8
        self._path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
        self.load_trajectory()

        # TODO: get wheelbase and keff from car
        self.controller = FDCAController(wheel_base=2.406, effective_ratio=1 / 13, human_compatible_reference=self._trajectory)

        self._bq_filter_velocity = LowPassFilterBiquad(fc=30, fs=100)
        self._bq_filter_heading = LowPassFilterBiquad(fc=30, fs=100)

        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self._error_old = np.array([0.0, 0.0])

        self.shared_variables.k_y = settings.k_y
        self.shared_variables.k_psi = settings.k_psi
        self.shared_variables.lohs = settings.lohs
        self.shared_variables.sohf = settings.sohf
        self.shared_variables.loha = settings.loha

        self.x_road_old = 0
        self.y_road_old = 0
        self.xdot_road_old = 0
        self.ydot_road_old = 0

        self.time = 0

        # threshold to check if a trajectory is circular in meters; subsequent points need to be 1 m of each other
        self.threshold_circular_trajectory = 1.0

    def load_trajectory(self):
        """Load HCR trajectory"""
        try:

            tmp = pd.read_csv(os.path.join(self._path_trajectory_directory, self.settings.trajectory_name))
            if not np.array_equal(tmp.values, self._trajectory):
                self._trajectory = tmp.values
            print('Loaded trajectory = ', self.settings.trajectory_name)
        except OSError as err:
            print('Error loading HCR trajectory file: ', err)

    def do(self, time_step_in_ns, carlainterface_shared_variables, hardware_manager_shared_variables, carla_interface_settings):
        """
        :param time_step_in_ns:
        :param carlainterface_shared_variables:
        :param hardware_manager_shared_variables:
        :param carla_interface_settings:
        :return:
        """

        for agent_settings in carla_interface_settings.agents.values():
            # try:
            if agent_settings.selected_controller == self.settings.__str__():
                if 'SensoDrive' in agent_settings.selected_input:
                    stiffness = hardware_manager_shared_variables.inputs[agent_settings.selected_input].auto_center_stiffness
                    steering_angle = hardware_manager_shared_variables.inputs[agent_settings.selected_input].steering_angle

                    # Compose a state containing the car information
                    car_state = np.array([[carlainterface_shared_variables.agents[agent_settings.__str__()].transform[0]],
                                          [carlainterface_shared_variables.agents[agent_settings.__str__()].transform[1]],
                                          [math.radians(carlainterface_shared_variables.agents[agent_settings.__str__()].transform[3])]])

                    # Compute control inputs using current position vector
                    self.shared_variables, torque_fdca = self.controller.compute_input(stiffness, steering_angle, car_state, self.shared_variables)
                    hardware_manager_shared_variables.inputs[agent_settings.selected_input].torque = torque_fdca
            # except:
            #     pass


class FDCAControllerSettings:
    def __init__(self, identifier=''):
        self.k_y = 0.2
        self.k_psi = 2
        self.lohs = 1
        self.sohf = 1.0
        self.loha = 1.0
        self.trajectory_name = "hcr_demomap.csv"
        self.identifier = identifier
        self.haptic_controller_type = HapticControllerTypes.FDCA.value

    def __str__(self):
        return str(self.identifier)

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class FDCAController:
    def __init__(self, wheel_base=2.406, effective_ratio=1/13, human_compatible_reference=None):
        self.wheel_base = wheel_base
        self.effective_ratio = effective_ratio
        self._trajectory = human_compatible_reference
        self._bq_filter_curve = LowPassFilterBiquad(fc=30, fs=100)

    def compute_input(self, stiffness, steering_angle, car_state, shared_variables):
        """
        Compute the control inputs for the FDCA Controller

        Args:
            stiffness (float): steering wheel stiffness
            steering_angle (float): current steering wheel angle
            car_state (numpy.ndarray): x, y and theta coordinates of car
            shared_variables (params): contains all information to be shared

        Returns:
            shared_variables (params): contains all information to be shared
            fdca_torque (float): computed control input
        """
        x_road, y_road, road_state, steering_reference = self._get_references(car_state)
        error = self._calculate_error(car_state, road_state)

        # Torques, 1. Feedforward torque with LOHS gain tuning, 2. Feedback torque with SOHF gain tuning, 3. Haptic authority (how much can I deviate from haptic system) with tunable LOHA stiffness
        feedforward_torque = shared_variables.lohs * (stiffness * steering_reference)  # LOHS torque (feedforward)
        feedback_torque = shared_variables.sohf * (shared_variables.k_y * error[0] + shared_variables.k_psi * error[1])  # SOHF torque (feedback)
        loha_torque = shared_variables.loha * ((feedforward_torque + feedback_torque) / stiffness - steering_angle)  # LOHA torque
        fdca_torque = feedforward_torque + feedback_torque + loha_torque

        # set the shared variables
        shared_variables.sw_des = (feedforward_torque + feedback_torque) / stiffness
        shared_variables.ff_torque = feedforward_torque
        shared_variables.fb_torque = feedback_torque
        shared_variables.loha_torque = loha_torque
        shared_variables.req_torque = fdca_torque
        shared_variables.lat_error = error[0]
        shared_variables.heading_error = error[1]
        shared_variables.x_road = x_road
        shared_variables.y_road = y_road

        return shared_variables, fdca_torque

    def _transform(self, x, theta):
        """
        Calculates rotation matrix and rotate vector x.

        Args:
            x (numpy.ndarray): vector to be rotated
            theta (float): Rotation angle

        Returns:
            np.ndarray: vector rotated around angle theta
        """
        R = np.array([[math.cos(theta), math.sin(theta), 0],
                      [-math.sin(theta), math.cos(theta), 0],
                      [0, 0, 1]])
        return np.matmul(R, x)

    def _calculate_error(self, car_state, road_state):
        """
        Calculate the controller error
        CARLA coordinate frame
        X: forward
        Y: right
        Z: upward
        Psi (heading): left-hand z-axis positive (yaw to the right is positive)
        Torque: rightward rotation is positive
        Args:
            car_state (numpy.ndarray): x, y and theta coordinate of car
            road_state (numpy.ndarray): x, y and theta coordinate of the road
        Returns:
            np.ndarray: vector containing the lateral error and heading error
        """
        error_state = road_state - car_state
        error_local_frame = self._transform(error_state, road_state[2, 0])  # Calculate error in road local frame

        # Make sure you dont get jumps (basically unwrap the angle with a threshold of pi radians (180 degrees))
        if error_local_frame[2, 0] > math.pi:
            error_local_frame[2, 0] = error_local_frame[2, 0] - 2.0 * math.pi
        if error_local_frame[2, 0] < -math.pi:
            error_local_frame[2, 0] = error_local_frame[2, 0] + 2.0 * math.pi

        return np.array([error_local_frame[1, 0], error_local_frame[2, 0]])

    def _heading(self, dx_dt, dy_dt):
        """
        Calculates the heading along a line.

        Args:
            dx_dt (numpy.ndarray): First derivative of x.
            dy_dt (numpy.ndarray): First derivative of y.

        Returns:
            np.ndarray: Heading along line in radians with respect to the world frame.
        """
        return np.arctan2(dy_dt, dx_dt)

    def _curvature(self, dx_dt, d2x_dt2, dy_dt, d2y_dt2):
        """
        Calculates the curvature along a line.

        Args:
            dx_dt (numpy.ndarray): First derivative of x.
            d2x_dt2 (numpy.ndarray): Second derivative of x.
            dy_dt (numpy.ndarray): First derivative of y.
            d2y_dt2 (numpy.ndarray): Second derivative of y.

        Returns:
            np.ndarray: Curvature along line.
        """
        return (dx_dt ** 2 + dy_dt ** 2) ** -1.5 * (dx_dt * d2y_dt2 - dy_dt * d2x_dt2)

    def _check_end(self, id):
        idx = []
        # Check if we are at the end of the trajectory
        for i in id:
            if i >= len(self._trajectory[:, 0]):
                idx.append(i - len(self._trajectory[:, 0]))
            else:
                idx.append(i)
        return idx

    def _get_references(self, car_state):
        """
        Function to obtain geometric information from the road and subsequently obtain reference steering angle

        Args:
            location (numpy.ndarray): x and y position of the car

        Returns:
            x (np.ndarray): Vector containing x coordinates of the (local) road
            y (np.ndarray): Vector containing y coordinates of the (local) road
            road_state (np.ndarray): Vector containing x, y and theta coordinate of the closes road point
            theta (float): Closest road point heading
            steering_reference (float): Steering wheel reference for closest road point
        """
        # gather data
        n = 50  # samples
        pos_car = [car_state[0, 0], car_state[1, 0]]
        id_now = find_closest_node(pos_car, self._trajectory[:, 1:3])
        s = list(range(n))
        id = s + id_now
        idx = self._check_end(id)
        x_road = self._trajectory[idx, 1]
        y_road = self._trajectory[idx, 2]

        data = np.array([x_road, y_road])
        smoothing_factor = 0.5
        # Cubic interpolation through generated midpoints to generate midline
        tck, _ = cp.interpolate.splprep(data, u=s, s=smoothing_factor)
        x, y = cp.interpolate.splev(s, tck, der=0)
        x_now, y_now = cp.interpolate.splev(0, tck, der=0)
        dx_dt, dy_dt = cp.interpolate.splev(20, tck, der=1)
        d2x_dt2, d2y_dt2 = cp.interpolate.splev(20, tck, der=2)

        theta = self._heading(dx_dt, dy_dt)
        curvature = self._curvature(dx_dt, d2x_dt2, dy_dt, d2y_dt2)
        curve_filtered = self._bq_filter_curve.step(curvature)
        road_state = np.array([[x_now], [y_now], [theta]])
        steering_reference = math.atan(self.wheel_base * curve_filtered) / self.effective_ratio

        return x, y, road_state, steering_reference

