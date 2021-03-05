import math
import os

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic

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
        self.slider_loha.valueChanged.connect(self._update_loha_slider_label)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)

        # hardcode lookahead time if someone needs it
        self.t_lookahead = 0

        self._loha_resolution = 50
        self.slider_loha.setMaximum(self._loha_resolution)
        self.spin_loha.setMaximum(self._loha_resolution)

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
        self.slider_loha.setValue(self.spin_loha.value())
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.loha = float(self.slider_loha.value())
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

    def _update_loha_slider_label(self):
        self.spin_loha.setValue(self.slider_loha.value())
        if self.checkbox_tuning_loha.isChecked():
            self.fdca_controller_settings.loha = float(self.slider_loha.value())
            self.lbl_loha.setText(str(self.fdca_controller_settings.loha))
            self.lbl_loha_deg.setText(str(round(math.radians(self.fdca_controller_settings.loha), 3)))
            try:
                self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].loha = self.fdca_controller_settings.loha
            except:
                pass

    def accept(self):
        self.slider_loha.setValue(self.spin_loha.value())
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.loha = float(self.slider_loha.value())
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
        self.slider_loha.setValue(settings_to_display.loha)
        self.spin_loha.setValue(settings_to_display.loha)

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
        self.t_lookahead = 0
        self._path_trajectory_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trajectories')
        self.load_trajectory()

        self._bq_filter_velocity = LowPassFilterBiquad(fc=30, fs=100)
        self._bq_filter_heading = LowPassFilterBiquad(fc=30, fs=100)
        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self._error_old = np.array([0.0, 0.0])

        self.shared_variables.k_y = settings.k_y
        self.shared_variables.k_psi = settings.k_psi
        self.shared_variables.lohs = settings.lohs
        self.shared_variables.sohf = settings.sohf
        self.shared_variables.loha = settings.loha

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
            return np.array([0,0])

        # if not vec_dir.any():
        #     error_heading = 0
        #     error_lat = 0
        #     return np.array([error_lat, error_heading])
        # find the lateral error. Project vec_car on the reference trajectory direction vector
        vec_error_lat = vec_car - (np.dot(vec_car, vec_dir) / np.dot(vec_dir, vec_dir)) * vec_dir
        error_lat = np.sqrt(np.dot(vec_error_lat, vec_error_lat))

        # calculate sign of error using the cross product
        e_sign = np.cross(vec_dir, vec_car)  # used to be e_sign = np.math.atan2(np.linalg.det([vec_dir, vec_car]), np.dot(vec_dir, vec_car))
        e_sign = -1.0 * e_sign / np.abs(e_sign)
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

    def _get_reference_sw_angle(self, t_ahead, location, velocity):
        future_location = location + velocity * t_ahead

        idx = find_closest_node(future_location, self._trajectory[:, 1:3])
        if idx >= len(self._trajectory) - 20:
            idx1 = 0
        else:
            idx1 = idx + 1

        # the trajectory is recorded in unitless steering angles (verify this in the csv)
        # so, we need to convert this to radians. First, multiply with 450 (1, -1) [-] = (450,-450) [deg]
        sw_angle_ff_des = math.radians(self._trajectory[idx1, 3] * 450)

        return sw_angle_ff_des

    def do(self, time_step_in_ns, carlainterface_shared_variables, hardware_manager_shared_variables, carla_interface_settings):
        """
        :param time_step_in_ns:
        :param carlainterface_shared_variables:
        :param hardware_manager_shared_variables:
        :param carla_interface_settings:
        :return:
        """

        for agent_settings in carla_interface_settings.agents.values():
            if agent_settings.selected_controller == self.settings.__str__():
                if 'SensoDrive' in agent_settings.selected_input:
                    stiffness = hardware_manager_shared_variables.inputs[agent_settings.selected_input].auto_center_stiffness

                    delta_t = time_step_in_ns / 1e9  # [s]

                    sw_angle = hardware_manager_shared_variables.inputs[agent_settings.selected_input].steering_angle

                    # extract data from CARLA
                    # CARLA coordinate system (left-handed coordinate system)
                    # X: forward
                    # Y: right
                    # Z: upward
                    # Psi (heading): left-hand z-axis positive (yaw to the right is positive)
                    # torque: rightward rotation is positive

                    pos_car = np.array([carlainterface_shared_variables.agents[agent_settings.__str__()].transform[0],
                                        carlainterface_shared_variables.agents[agent_settings.__str__()].transform[1]])
                    vel_car = np.array([carlainterface_shared_variables.agents[agent_settings.__str__()].velocities[0],
                                        carlainterface_shared_variables.agents[agent_settings.__str__()].velocities[1]])

                    heading_car = carlainterface_shared_variables.agents[agent_settings.__str__()].transform[3]

                    # find static error and error rate:
                    error = self.calculate_error(pos_car, heading_car, vel_car)
                    error_rate = (error - self._error_old) / delta_t

                    # filter the error rate with biquad filter
                    error_rate_filtered = np.array([0.0, 0.0])
                    error_rate_filtered[0] = self._bq_filter_velocity.step(error_rate[0])
                    error_rate_filtered[1] = self._bq_filter_heading.step(error_rate[1])

                    # put errors in 1 variable
                    self._controller_error[0:2] = error
                    self._controller_error[2:4] = error_rate_filtered

                    # FDCA specific calculations here
                    # strength of haptic feedback
                    sw_angle_fb = self.shared_variables.sohf * (
                                self.shared_variables.k_y * self._controller_error[0] + self.shared_variables.k_psi * self._controller_error[1])

                    # get feedforward sw angle
                    sw_angle_ff_des = self._get_reference_sw_angle(self.t_lookahead, pos_car, vel_car)

                    # level of haptic support (feedforward); get sw angle needed for haptic support
                    sw_angle_ff = self.shared_variables.lohs * sw_angle_ff_des

                    # calculate torques

                    # loha torque
                    # calculate sw error; BASED ON BASTIAAN PETERMEIJER's SIMULINK IMPLEMENTATION OF THE FDCA
                    # add fb and ff sw angles to get total desired sw angle; this is the sw angle the sw should get
                    delta_sw = (sw_angle_fb + sw_angle_ff_des) - sw_angle

                    torque_loha = delta_sw * self.shared_variables.loha  # loha should be [Nm/rad]

                    # feedforward/feedback torque
                    sw_angle_ff_fb = sw_angle_ff + sw_angle_fb

                    # simplified inverse steering dynamics

                    # check: the inherent SW stiffness should not be zero (div by 0)
                    if abs(stiffness) < 0.001:
                        stiffness = 0.001

                    torque_ff_fb = sw_angle_ff_fb * 1.0 / (1.0 / stiffness)  # !!! stiffness should be in [Nm/rad]

                    # total torque of FDCA, to be sent to SW controller in Nm
                    torque_fdca = torque_loha + torque_ff_fb

                    # update variables
                    self._error_old = error

                    hardware_manager_shared_variables.inputs[agent_settings.selected_input].torque = torque_fdca

                    # set the shared variables
                    self.shared_variables.lat_error = error[0]
                    self.shared_variables.heading_error = error[1]
                    self.shared_variables.sw_des = sw_angle_ff_des + sw_angle_fb
                    self.shared_variables.ff_torque = sw_angle_ff * stiffness
                    self.shared_variables.fb_torque = sw_angle_fb * stiffness
                    self.shared_variables.loha_torque = torque_loha
                    self.shared_variables.req_torque = torque_fdca


class FDCAControllerSettings:
    def __init__(self, identifier=''):
        self.t_lookahead = 0.0
        self.k_y = 0.15
        self.k_psi = 2.5
        self.lohs = 1.0
        self.sohf = 1.0
        self.loha = 0.0
        self.trajectory_name = "MiddleRoadTVRecord_filtered_ffswang_heading_3hz.csv"
        self.identifier = identifier

        self.haptic_controller_type = HapticControllerTypes.FDCA.value

    def __str__(self):
        return str(self.identifier)

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
