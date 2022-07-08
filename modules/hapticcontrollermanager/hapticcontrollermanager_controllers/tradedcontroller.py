import math
import os

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic

from core.statesenum import State
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes
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
        # self.slider_loha.setValue(self.spin_loha.value())
        self.traded_controller_settings.k_y = float(self.edit_k_y.text())
        self.traded_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.traded_controller_settings.kd_y = float(self.edit_kd_y.text())
        self.traded_controller_settings.kd_psi = float(self.edit_kd_psi.text())
        self.traded_controller_settings.alpha = float(self.edit_alpha.text())
        self.traded_controller_settings.tau_th = float(self.edit_tau_th.text())
        self.traded_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        try:
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].k_y = self.traded_controller_settings.k_y
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].k_psi = self.traded_controller_settings.k_psi
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].kd_y = self.traded_controller_settings.kd_y
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].kd_psi = self.traded_controller_settings.kd_psi
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].alpha = self.traded_controller_settings.alpha
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].tau_th = self.traded_controller_settings.tau_th
        except:
            pass

        self._display_values()


    def accept(self):
        # self.slider_loha.setValue(self.spin_loha.value())
        self.traded_controller_settings.k_y = float(self.edit_k_y.text())
        self.traded_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.traded_controller_settings.kd_y = float(self.edit_kd_y.text())
        self.traded_controller_settings.kd_psi = float(self.edit_kd_psi.text())
        self.traded_controller_settings.alpha = float(self.edit_alpha.text())
        self.traded_controller_settings.tau_th = float(self.edit_tau_th.text())
        self.traded_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        try:
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].k_y = self.traded_controller_settings.k_y
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].k_psi = self.traded_controller_settings.k_psi
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].kd_y = self.traded_controller_settings.kd_y
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].kd_psi = self.traded_controller_settings.kd_psi
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].alpha = self.traded_controller_settings.alpha
            self.module_manager.shared_variables.haptic_controllers[self.traded_controller_settings.identifier].tau_th = self.traded_controller_settings.tau_th
        except:
            pass

        super().accept()

    def _display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.traded_controller_settings

        # update the current controller settings
        self.lbl_k_y.setText(str(settings_to_display.k_y))
        self.lbl_k_psi.setText(str(settings_to_display.k_psi))
        self.lbl_kd_y.setText(str(settings_to_display.kd_y))
        self.lbl_kd_psi.setText(str(settings_to_display.kd_psi))
        self.lbl_alpha.setText(str(settings_to_display.alpha))
        self.lbl_tau_th.setText(str(settings_to_display.tau_th))

        self.edit_k_y.setText(str(settings_to_display.k_y))
        self.edit_k_psi.setText(str(settings_to_display.k_psi))
        self.edit_kd_y.setText(str(settings_to_display.kd_y))
        self.edit_kd_psi.setText(str(settings_to_display.kd_psi))
        self.edit_alpha.setText(str(settings_to_display.alpha))
        self.edit_tau_th.setText(str(settings_to_display.tau_th))

        idx_traj = self.cmbbox_hcr_selection.findText(settings_to_display.trajectory_name)
        self.cmbbox_hcr_selection.setCurrentIndex(idx_traj)

    def _set_default_values(self):
        self._display_values(HapticControllerTypes.TradedControl.settings())
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

        # filtering
        self.frequency = 100
        self._bq_filter_velocity = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_heading = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_angle = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_des = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_acc = LowPassFilterBiquad(fc=10, fs=self.frequency)

        # Error states
        self._controller_error = np.array([[0.0, 0.0, 0.0, 0.0]])
        self._error_old = np.array([0.0, 0.0])
        self._sw_des_old = 0

        # Observer dynamics
        self.Gamma = 20 * np.array([[2, 0], [0, 2]])
        self.alpha = 2.5
        self.kappa = 1
        self.human_estimated_torque = 0.0
        self.x_hat = np.array([[0.0], [0.0]])
        self._old_sw_angle = 0.0
        self._old_sw_rate = 0.0

        # Shared variables for Traded Control
        self.shared_variables.k_y = settings.k_y
        self.shared_variables.k_psi = settings.k_psi
        self.shared_variables.kd_y = settings.kd_y
        self.shared_variables.kd_psi = settings.kd_psi
        self.shared_variables.alpha = settings.alpha
        self.shared_variables.tau_th = settings.tau_th
        self.torque_threshold = self.shared_variables.tau_th
        self.alpha = self.shared_variables.alpha
        self.controller_gains = np.array([[self.shared_variables.k_y],
                                          [self.shared_variables.k_psi],
                                          [self.shared_variables.kd_y],
                                          [self.shared_variables.kd_psi]])

        self.time = 0

        # threshold to check if a trajectory is circular in meters; subsequent points need to be 1 m of each other
        self.threshold_circular_trajectory = 1.0

    def do(self, time_step_in_ns, carlainterface_shared_variables, hardware_manager_shared_variables, carla_interface_settings):
        """
        :param time_step_in_ns:
        :param carlainterface_shared_variables:
        :param hardware_manager_shared_variables:
        :param carla_interface_settings:
        :return:
        """

        # Ensure good initialisation of time


        for agent_settings in carla_interface_settings.agents.values():
            if agent_settings.selected_controller == self.settings.__str__():
                if 'SensoDrive' in agent_settings.selected_input:
                    stiffness = hardware_manager_shared_variables.inputs[agent_settings.selected_input].auto_center_stiffness
                    delta_t = time_step_in_ns / 1e9  # [s]
                    self.time += delta_t

                    # Steering Wheel Information
                    sw_angle = hardware_manager_shared_variables.inputs[agent_settings.selected_input].steering_angle
                    sw_rate_unf = (sw_angle - self._old_sw_angle) / delta_t
                    sw_rate = self._bq_filter_angle.step(sw_rate_unf)
                    sw_acc = self._bq_filter_acc.step((sw_rate - self._old_sw_rate) / delta_t)
                    sw_state = np.array([sw_angle, sw_rate, sw_acc])
                    self._old_sw_angle = sw_angle
                    self._old_sw_rate = sw_rate_unf

                    # TODO: Remove to init
                    # Steering wheel dynamic model
                    # Dynamics
                    Jw = 0.04876200657888505
                    Bw = hardware_manager_shared_variables.inputs[agent_settings.selected_input].damping
                    Kw = hardware_manager_shared_variables.inputs[agent_settings.selected_input].auto_center_stiffness
                    self.A = np.array([[0, 1], [- Kw / Jw, - Bw / Jw]])
                    self.B = np.array([[0], [1 / Jw]])

                    # Car information
                    # extract data from CARLA
                    # CARLA coordinate system (left-handed coordinate system)
                    # X: forward
                    # Y: right
                    # Z: upward
                    # Psi (heading): left-hand z-axis positive (yaw to the right is positive)
                    # torque: rightward rotation is positive
                    pos_car = np.array([carlainterface_shared_variables.agents[agent_settings.__str__()].transform[0],
                                        carlainterface_shared_variables.agents[agent_settings.__str__()].transform[1]])
                    vel_car = np.array([carlainterface_shared_variables.agents[agent_settings.__str__()].velocities_in_world_frame[0],
                                        carlainterface_shared_variables.agents[agent_settings.__str__()].velocities_in_world_frame[1]])
                    heading_car = carlainterface_shared_variables.agents[agent_settings.__str__()].transform[3]

                    # find static error and error rate:
                    error = self.calculate_error(pos_car, heading_car, vel_car)
                    error_rate = (error - self._error_old) / delta_t

                    # filter the error rate with biquad filter
                    error_rate_filtered = np.array([0.0, 0.0])
                    error_rate_filtered[0] = self._bq_filter_velocity.step(error_rate[0])
                    error_rate_filtered[1] = self._bq_filter_heading.step(error_rate[1])

                    # put errors in 1 variable
                    self._controller_error[0, 0:2] = error
                    self._controller_error[0, 2:4] = error_rate_filtered

                    # check: the inherent SW stiffness should not be zero (div by 0)
                    if abs(stiffness) < 0.001:
                        stiffness = 0.001

                    sw_des = self._get_reference_sw_angle(pos_car)
                    sw_des_rate = self._bq_filter_des.step((sw_des - self._sw_des_old) / delta_t)
                    self._sw_des_old = sw_des
                    sw_des_state = np.array([sw_des, sw_des_rate])

                    # Wait 1 sec to ensure good initalization
                    # set initial values
                    if self.time < 1:
                        authority = 0
                        feedforward_torque = 0
                        feedback_torque = 0
                        self.human_estimated_torque = 0
                        self.x_hat = np.array([[sw_state[0] - sw_des], [sw_state[1] - sw_des_rate]])
                    else:
                        authority = self.compute_authority(delta_t)
                        self.estimate_human_control(sw_state, sw_des_state, delta_t)
                        feedback_torque = self.compute_torque(self._controller_error)

                    if authority > 0.2:
                        torque = authority * (feedback_torque + stiffness * sw_des)
                    else:
                        torque = 0
                    x = np.array([[sw_angle], [sw_rate]])
                    nonlin = self.nonlinear_term(x)
                    self.torque = min(max(torque, -3), 3)
                    # feedforward_torque = stiffness * sw_des
                    feedforward_torque = 0

                    # update variables
                    self._error_old = error
                    hardware_manager_shared_variables.inputs[agent_settings.selected_input].torque = self.torque - nonlin

                    # set the shared variables
                    self.shared_variables.lat_error = error[0]
                    self.shared_variables.heading_error = error[1]
                    self.shared_variables.sw_des = sw_des
                    self.shared_variables.ff_torque = feedforward_torque
                    self.shared_variables.fb_torque = feedback_torque
                    self.shared_variables.req_torque = self.torque
                    self.shared_variables.authority = authority
                    self.shared_variables.estimated_human_torque = self.human_estimated_torque

    def load_trajectory(self):
        """Load HCR trajectory"""
        try:

            tmp = pd.read_csv(os.path.join(self._path_trajectory_directory, self.settings.trajectory_name))
            if not np.array_equal(tmp.values, self._trajectory):
                self._trajectory = tmp.values
            print('Loaded trajectory = ', self.settings.trajectory_name)
        except OSError as err:
            print('Error loading HCR trajectory file: ', err)

    def nonlinear_term(self, x):

        g = 9.81
        m = 0.25577512040264017
        dh = 0.08868507357869222
        dl = 0.0207971806237164
        vt = 0.3578151261152145
        vsp = 2 * vt
        tau_d = -0.11322530785321677
        tau_fric = 0.031177592111752105

        # Gravity
        tau_g = - m * g * dh * np.sin(x[0, 0]) - m * g * dl * np.cos(x[0, 0])

        # Friction
        v = x[1, 0]
        gv = v / vsp * np.exp(-(v / (np.sqrt(2) * vsp)) ** 2 + 1 / 2)
        fc = tau_d * np.tanh(v / vt)
        tau_f = gv * tau_fric + fc
        return tau_f + tau_g

    def calculate_error(self, pos_car, heading_car, vel_car=np.array([0.0, 0.0])):
        """
        Calculate the controller error
        CARLA coordinate frame
        X: forward
        Y: right
        Z: upward
        Psi (heading): left-hand z-axis positive (yaw to the right is positive)
        Torque: rightward rotation is positive
        :param pos_car:
        :param heading_car:
        :param vel_car:
        :return:
        """
        pos_car = pos_car + vel_car * self.t_lookahead  # linear extrapolation, should be updated

        # Find waypoint index of the point that the car would be in the future (compared to own driven trajectory)
        index_closest_waypoint = find_closest_node(pos_car, self._trajectory[:, 1:3])

        # circular: if end of the trajectory, go back to the first one; note that this is risky, if the reference trajectory is not circular!
        if index_closest_waypoint >= len(self._trajectory) - 1:
            if np.linalg.norm(self._trajectory[0, 1:3] - self._trajectory[index_closest_waypoint, 1:3]) < self.threshold_circular_trajectory:
                index_closest_waypoint_next = 0
            else:
                index_closest_waypoint_next = index_closest_waypoint
        else:
            index_closest_waypoint_next = index_closest_waypoint + 1

            # Some trajectories have multiple subsequent waypoints at the same position, this while loop increments the next index until a new waypoint is found
            while (self._trajectory[index_closest_waypoint, 1:3] == self._trajectory[index_closest_waypoint_next, 1:3]).all():
                index_closest_waypoint_next += 1
                if index_closest_waypoint >= len(self._trajectory):
                    break

        # calculate lateral error
        pos_ref = self._trajectory[index_closest_waypoint, 1:3]
        pos_ref_next = self._trajectory[index_closest_waypoint_next, 1:3]

        vec_car = pos_car - pos_ref
        vec_dir = pos_ref_next - pos_ref

        if not vec_dir.any():
            print(index_closest_waypoint, index_closest_waypoint_next, pos_ref, pos_ref_next)
            return np.array([0, 0])

        # if not vec_dir.any():
        #     error_heading = 0
        #     error_lat = 0
        #     return np.array([error_lat, error_heading])
        # find the lateral error. Project vec_car on the reference trajectory direction vector
        vec_error_lat = vec_car - (np.dot(vec_car, vec_dir) / np.dot(vec_dir, vec_dir)) * vec_dir
        error_lat = np.sqrt(np.dot(vec_error_lat, vec_error_lat))

        # calculate sign of error using the cross product
        e_sign = np.cross(vec_dir, vec_car)  # used to be e_sign = np.math.atan2(np.linalg.det([vec_dir, vec_car]), np.dot(vec_dir, vec_car))
        if np.abs(e_sign) < 0.0001:
            e_sign = -1.0 * e_sign / np.abs(e_sign + 0.001)
        else:
            e_sign = -1.0 * e_sign / np.abs(e_sign)
        # e_sign = np.math.atan2(np.linalg.det([vec_dir, vec_car]), np.dot(vec_dir, vec_car))
        error_lat *= e_sign

        # calculate heading error: left-handed CW positive
        heading_ref = self._trajectory[index_closest_waypoint, 6]

        error_heading = math.radians(heading_ref) - math.radians(heading_car)  # in radians

        # Make sure you dont get jumps (basically unwrap the angle with a threshold of pi radians (180 degrees))
        if error_heading > math.pi:
            error_heading = error_heading - 2.0 * math.pi
        if error_heading < -math.pi:
            error_heading = error_heading + 2.0 * math.pi

        return np.array([error_lat, error_heading])

    def estimate_human_control(self, sw_state, sw_des_state, delta_t):
        # # sw_state[0] = sw_angle, sw_state[1] = sw_rate, sw_state[2] = sw_acc
        # # Compose states
        xi = np.array([[sw_state[0] - sw_des_state[0]], [sw_state[1] - sw_des_state[1]]])
        x = np.array([[sw_state[0]], [sw_state[1]]])
        xi_dot = np.array([[sw_state[1]], [sw_state[2]]])
        xi_tilde = self.x_hat - x
        x_hat_dot = np.matmul(self.A, self.x_hat) + self.B * (self.torque + self.human_estimated_torque) - np.matmul(self.Gamma, xi_tilde)
        # # print("measured angle, estimated angle", sw_state[0], self.x_hat[0])
        # # print("measured speed, estimated speed", sw_state[1], self.x_hat[1])
        # # print("measured acc, estimated acc", sw_state[2], x_hat_dot[1])
        # xi_tilde_dot = x_hat_dot - x_dot
        # # print(xi_tilde, xi_tilde_dot)
        #
        # # Update law for observing human input
        # # m_squared = 1 + self.kappa * np.matmul(xi.transpose(), xi)
        # # Bu_tilde = xi_tilde_dot - (np.matmul((self.A - self.Gamma), xi_tilde))
        # # print("butilde ", Bu_tilde)
        # # print("error ", xi)
        # # human_estimated_torque_update = self.alpha * np.matmul(xi.transpose(), Bu_tilde) / m_squared
        #
        # pseudo_B = 1 / (np.matmul(self.B.transpose(), self.B)) * self.B.transpose()
        # u_h_tilde = np.matmul(pseudo_B, (xi_tilde_dot - (np.matmul((self.A - self.Gamma), xi_tilde))))
        # m_squared = 1 + self.kappa * np.matmul(xi.transpose(), xi)
        # Lhhat_dot = u_h_tilde / m_squared * xi.transpose() * self.alpha
        # human_estimated_torque_update = np.matmul(-Lhhat_dot, xi)
        #
        # # human_estimated_torque_update = np.matmul(xi.transpose(), (xi_tilde_dot - (np.matmul((self.A - self.Gamma), xi_tilde)))) * self.alpha / m_squared
        # self.human_estimated_torque += human_estimated_torque_update * delta_t
        # self.x_hat += x_hat_dot * delta_t
        # # print("xi, xi_hat, xi_tilde ", xi, self.xi_hat, xi_tilde)
        # # print("update function: ", human_estimated_torque_update)

        # self.human_estimated_torque = np.matmul(pseudo_B, xi_dot - np.matmul(self.A, xi) - np.matmul(self.B, np.array([[self.torque]])))
        self.human_estimated_torque += - self.alpha * np.matmul(xi_tilde.transpose(), self.B) * delta_t
        self.x_hat += x_hat_dot * delta_t

        print("estimated torque: ", self.human_estimated_torque)
        # print("measured error, measured error rate, current rate: ", xi[0], xi[1], xi_dot[0], xi_dot[1])
        # print("estimated error, error rate and error acceleration: ", self.xi_hat[0], self.xi_hat[1], xi_hat_dot[0], xi_hat_dot[1])

    def compute_torque(self, controller_error):
        feedback_torque = np.matmul(controller_error, self.controller_gains)
        return feedback_torque

    def compute_authority(self, delta_t):
        # See if the threshold is crossed and if so increase authority
        # print("torque vs threshold ", self.estimated_human_torque, self.torque_threshold)
        if self.human_estimated_torque ** 2 < self.torque_threshold ** 2:
            direction = 2  # Increase authority
        else:
            direction = -2  # Decrease authority
            # print("getting here ever?")
        self.x_ += delta_t * direction
        self.x_ = min(max(self.x_, -0.2), 3.2)
        authority = 1 - math.tanh(self.x_)
        authority = min(max(authority, 0), 1)
        print("lambda = ", authority)
        return authority

    def _get_reference_sw_angle(self, location):
        idx = find_closest_node(location, self._trajectory[:, 1:3])
        if idx >= len(self._trajectory) - 20:
            idx1 = 0
        else:
            idx1 = idx + 1

        # the trajectory is recorded in unitless steering angles (verify this in the csv)
        # so, we need to convert this to radians. First, multiply with 450 (1, -1) [-] = (450,-450) [deg]
        sw_angle_ff_des = math.radians(self._trajectory[idx1, 3] * 450)

        return sw_angle_ff_des


class TradedControllerSettings:
    def __init__(self, identifier=''):
        self.t_lookahead = 0.0
        self.k_y = 0.15
        self.k_psi = 2.5
        self.kd_y = 0.05
        self.kd_psi = 1.0
        self.alpha = 2.0
        self.tau_th = 0.1
        self.trajectory_name = "hcr_trajectory.csv"
        self.identifier = identifier

        self.haptic_controller_type = HapticControllerTypes.TradedControl.value

    def __str__(self):
        return str(self.identifier)

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
