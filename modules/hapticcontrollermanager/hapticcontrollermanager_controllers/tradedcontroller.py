import math
import os

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic

from core.statesenum import State
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes
from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAController
from tools import LowPassFilterBiquad
from tools.haptic_controller_tools import find_closest_node


class TradedControllerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings, module_manager, parent=None):
        super().__init__(parent)

        self.traded_controller_settings = settings
        self.module_manager = module_manager

        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/tradedcontroller_settings_ui.ui"), self)
        self._path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
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
        self.traded_controller_settings.alpha = self.spinbox_alpha.value()
        self.traded_controller_settings.tau_th = self.spinbox_tau.value()
        if self.checkInvert.isChecked():
            self.traded_controller_settings.gamma = 1
        else:
            self.traded_controller_settings.gamma = -1
        self.traded_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        try:
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].alpha = self.traded_controller_settings.alpha
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].tau_th = self.traded_controller_settings.tau_th
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].gamma = self.traded_controller_settings.gamma
        except AttributeError:
            pass

        self._display_values()


    def accept(self):
        self.traded_controller_settings.alpha = self.spinbox_alpha.value()
        self.traded_controller_settings.tau_th = self.spinbox_tau.value()
        if self.checkInvert.isChecked():
            self.traded_controller_settings.gamma = 1
        else:
            self.traded_controller_settings.gamma = -1
        self.traded_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        try:
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].alpha = self.traded_controller_settings.alpha
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].tau_th = self.traded_controller_settings.tau_th
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].gamma = self.traded_controller_settings.gamma
        except AttributeError:
            pass

        super().accept()

    def _display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.traded_controller_settings

        # update the current controller settings
        self.lbl_alpha.setText(str(settings_to_display.alpha))
        self.lbl_tau_th.setText(str(settings_to_display.tau_th))

        self.spinbox_alpha.setValue(settings_to_display.alpha)
        self.spinbox_tau.setValue(settings_to_display.tau_th)

        idx_traj = self.cmbbox_hcr_selection.findText(settings_to_display.trajectory_name)
        self.cmbbox_hcr_selection.setCurrentIndex(idx_traj)

    def _set_default_values(self):
        self._display_values(HapticControllerTypes.TRADED_CONTROL.settings())
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

        idx = self.cmbbox_hcr_selection.findText(self.traded_controller_settings.trajectory_name)
        if idx != -1:
            self.cmbbox_hcr_selection.setCurrentIndex(idx)


class TradedControllerProcess:
    def __init__(self, settings, shared_variables, carla_interface_settings):
        self.settings = settings
        self.carla_interface_settings = carla_interface_settings
        self.shared_variables = shared_variables
        self._trajectory = None
        self.t_lookahead = 0
        self.x_ = 0
        self.estimated_human_torque = 0
        self.torque = 0
        self._path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
        self.load_trajectory()

        self.controller = FDCAController(wheel_base=2.406, effective_ratio=1 / 13, human_compatible_reference=self._trajectory)

        # filtering
        self.frequency = 100
        self._bq_filter_velocity = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_heading = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_rate = LowPassFilterBiquad(fc=25, fs=self.frequency)

        # Controller states
        self._old_steering_angle = 0

        # Observer dynamics
        self.damping = 0
        self.stiffness = 0
        self.inertia = 0.04876200657888505
        self.observer_matrix = 20 * np.array([[2, 0], [0, 2]])
        self.alpha = 2.5
        self.kappa = 1
        self.human_estimated_torque = 0.0
        self.x_hat = np.array([[0.0], [0.0]])

        # Shared variables for Traded Control
        self.shared_variables.k_y = settings.k_y
        self.shared_variables.k_psi = settings.k_psi
        self.shared_variables.lohs = settings.lohs
        self.shared_variables.sohf = settings.sohf
        self.shared_variables.loha = settings.loha
        self.shared_variables.alpha = settings.alpha
        self.shared_variables.tau_th = settings.tau_th
        self.shared_variables.gamma = settings.gamma
        self.torque_threshold = self.shared_variables.tau_th
        self.alpha = self.shared_variables.alpha
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
            if agent_settings.selected_controller == str(self.settings):
                if 'SensoDrive' in agent_settings.selected_input:
                    self.stiffness = hardware_manager_shared_variables.inputs[agent_settings.selected_input].auto_center_stiffness
                    self.damping = hardware_manager_shared_variables.inputs[agent_settings.selected_input].damping
                    delta_t = time_step_in_ns / 1e9  # [s]
                    steering_angle = hardware_manager_shared_variables.inputs[agent_settings.selected_input].steering_angle

                    # Compose a state containing the car information
                    car_state = np.array([[carlainterface_shared_variables.agents[agent_settings.__str__()].transform[0]],
                                          [carlainterface_shared_variables.agents[agent_settings.__str__()].transform[1]],
                                          [math.radians(carlainterface_shared_variables.agents[agent_settings.__str__()].transform[3])]])

                    # Compute control inputs using current position vector
                    self.shared_variables, torque_fdca = self.controller.compute_input(self.stiffness, steering_angle, car_state, self.shared_variables)
                    torque_tc = self.compute_tc(torque_fdca, steering_angle, delta_t)
                    hardware_manager_shared_variables.inputs[agent_settings.selected_input].torque = torque_tc

                    # Set the shared variables
                    self.shared_variables.estimated_human_torque = self.human_estimated_torque

    def compute_tc(self, torque_fdca, steering_angle, timestep):
        """
        inputs
            torque_fdca (float): torque computed using the FDCA controller which yields a stable trajectory
            steering_angle (float): Steering angle of the SensoDrive
            timestep (float): Time since last computations

        outputs
            torque (float): output steering torque, with nonlinear component compensation
        """
        steering_state = self._compute_steering_states(steering_angle, timestep)
        nonlinear_component = self._compute_nonlinear_torques(steering_state)
        self._estimate_human_control(steering_state, timestep)
        authority = self._compute_authority(delta_t=timestep)
        self.torque = torque_fdca * authority
        return self.torque - nonlinear_component

    def _compute_steering_states(self, steering_angle, timestep):
        # Compute steering wheel states, mainly just steering rate
        unfiltered_steering_rate = (steering_angle - self._old_steering_angle) / timestep
        steering_rate = self._bq_filter_rate.step(unfiltered_steering_rate)
        steering_state = np.array([[steering_angle], [steering_rate]])
        self._old_steering_angle = steering_angle
        return steering_state

    def _system_matrices(self):
        # Compute system matrices from steering wheel parameters
        A = np.array([[0, 1], [- self.stiffness / self.inertia, - self.damping / self.inertia]])
        B = np.array([[0], [1 / self.inertia]])
        return A, B

    def _estimate_human_control(self, steering_state, delta_t):
        # Compose states
        A, B = self._system_matrices()
        x = steering_state
        xi_tilde = self.x_hat - x
        x_hat_dot = np.matmul(A, self.x_hat) + B * (self.torque + self.human_estimated_torque) - np.matmul(self.observer_matrix, xi_tilde)
        self.human_estimated_torque += - self.alpha * np.matmul(xi_tilde.transpose(), B) * delta_t
        self.x_hat += x_hat_dot * delta_t

    def _compute_authority(self, delta_t):
        # See if the threshold is crossed and if so increase authority
        if self.human_estimated_torque ** 2 < self.torque_threshold ** 2:
            direction = 1  # Increase authority
        else:
            direction = -1  # Decrease authority
        self.x_ += delta_t * direction * self.shared_variables.gamma
        self.x_ = min(max(self.x_, -0.5), 3)
        c1 = 3
        c2 = 0.5
        authority = 1 - (1 + math.exp(-c1 * (self.x_ - c2))) ** -1
        authority = min(max(authority, 0), 1)
        return authority

    def _compute_nonlinear_torques(self, x):
        """
        This function is used to do feedforward compensation of nonlinear torques due to gravity and friction, to use a linear system for computing human input torques.
            inputs
                x (np.array): System states composed of steering angle and steering rate

            outputs
                nonlinear_torques (float): output torque composed of gravity and friction torque.
        """
        g = 9.81
        m = 0.25577512040264017
        dh = 0.08868507357869222
        dl = 0.0207971806237164
        vt = 0.3578151261152145
        vsp = 2 * vt
        tau_d = -0.11322530785321677
        tau_fric = 0.031177592111752105

        # Gravity
        tau_g = - m * g * dh * np.sin(x[0]) - m * g * dl * np.cos(x[0])

        # Friction
        v = x[1]
        gv = v / vsp * np.exp(-(v / (np.sqrt(2) * vsp)) ** 2 + 1 / 2)
        fc = tau_d * np.tanh(v / vt)
        tau_f = gv * tau_fric + fc
        nonlinear_torques = tau_f + tau_g
        return nonlinear_torques

class TradedControllerSettings:
    def __init__(self, identifier=''):
        self.k_y = 0.2
        self.k_psi = 2
        self.lohs = 1
        self.sohf = 1.0
        self.loha = 1.0
        self.alpha = 2.0
        self.tau_th = 0.1
        self.gamma = -1
        self.trajectory_name = "hcr_trajectory.csv"
        self.identifier = identifier
        self.haptic_controller_type = HapticControllerTypes.TRADED_CONTROL.value

    def __str__(self):
        return str(self.identifier)

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
