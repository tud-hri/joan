import math
import os

import numpy as np
import pandas as pd
import scipy as cp
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt

from core.statesenum import State
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes
from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.torque_sensor import TorqueSensor
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
        self.fdca_controller_settings.k_y = self.spinbox_ky.value()
        self.fdca_controller_settings.k_psi = self.spinbox_kpsi.value()
        self.fdca_controller_settings.lohs = self.spinbox_lohs.value()
        self.fdca_controller_settings.sohf = self.spinbox_sohf.value()
        self.fdca_controller_settings.loha = self.spinbox_loha.value()
        self.fdca_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())
        try:
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_y = self.fdca_controller_settings.k_y
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_psi = self.fdca_controller_settings.k_psi
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].lohs = self.fdca_controller_settings.lohs
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].sohf = self.fdca_controller_settings.sohf
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].loha = self.fdca_controller_settings.loha
        except AttributeError:
            pass

        self._display_values()

    def accept(self):
        self.fdca_controller_settings.k_y = self.spinbox_ky.value()
        self.fdca_controller_settings.k_psi = self.spinbox_kpsi.value()
        self.fdca_controller_settings.lohs = self.spinbox_lohs.value()
        self.fdca_controller_settings.sohf = self.spinbox_sohf.value()
        self.fdca_controller_settings.loha = self.spinbox_loha.value()
        self.fdca_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())
        try:
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_y = self.fdca_controller_settings.k_y
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].k_psi = self.fdca_controller_settings.k_psi
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].lohs = self.fdca_controller_settings.lohs
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].sohf = self.fdca_controller_settings.sohf
            self.module_manager.shared_variables.haptic_controllers[self.fdca_controller_settings.identifier].loha = self.fdca_controller_settings.loha
        except AttributeError:
            pass
        except KeyError:
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

        self.spinbox_ky.setValue(settings_to_display.k_y)
        self.spinbox_kpsi.setValue(settings_to_display.k_psi)
        self.spinbox_lohs.setValue(settings_to_display.lohs)
        self.spinbox_sohf.setValue(settings_to_display.sohf)
        self.spinbox_loha.setValue(settings_to_display.loha)

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
        self.load_trajectory(selected_trajectory=0)

        # TODO: get wheelbase and keff from car
        self.controller = FDCAController(wheel_base=2.406, effective_ratio=1/13, human_compatible_reference=self._trajectory)
        self.torque_sensor = TorqueSensor()

        self._bq_filter_velocity = LowPassFilterBiquad(fc=25, fs=100)
        self._bq_filter_heading = LowPassFilterBiquad(fc=25, fs=100)
        # self._bq_filter_torque = LowPassFilterBiquad(fc=5, fs=100)

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
        self.torque_fdca = 0.0

        self.first_time = True
        self.trajectory_number = 0

        # threshold to check if a trajectory is circular in meters; subsequent points need to be 1 m of each other
        self.threshold_circular_trajectory = 1.0

    def load_trajectory(self, selected_trajectory):
        """Load HCR trajectory"""
        print("loading HCR trajectory")
        if self.carla_interface_settings.agents["Ego Vehicle_1"].random_trajectory:
            if selected_trajectory > 0:
                self.trajectory_number = selected_trajectory
            else:
                self.trajectory_number = self.carla_interface_settings.agents["Ego Vehicle_1"].selected_trajectory

            print("take trajectory ", self.trajectory_number)
            if self.trajectory_number == 2:
                self.settings.trajectory_name = "crash_npc2.csv"
            elif self.trajectory_number == 3:
                self.settings.trajectory_name = "crash_npc3.csv"
            elif self.trajectory_number == 4:
                self.settings.trajectory_name = "crash_npc4.csv"
            elif self.trajectory_number == 5:
                self.settings.trajectory_name = "crash_npc5.csv"
            else:
                print("this is odd")

        if selected_trajectory > 0:
            try:
                tmp = pd.read_csv(os.path.join(self._path_trajectory_directory, self.settings.trajectory_name))
                # self._trajectory=None
                if not np.array_equal(tmp.values, self._trajectory):
                    self._trajectory = tmp.values
                    print('Loaded trajectory = ', self.settings.trajectory_name)
                else:
                    print("goes wrong?")
            except OSError as err:
                print('Error loading HCR trajectory file: ', err)
        else:
            print("waiting to hand the correct trajectory")

    def do(self, time_step_in_ns, carlainterface_shared_variables, hardware_manager_shared_variables, carla_interface_settings):
        """
        :param time_step_in_ns:
        :param carlainterface_shared_variables:
        :param hardware_manager_shared_variables:
        :param carla_interface_settings:
        :return:
        """
        selected_trajectory = carlainterface_shared_variables.agents['Ego Vehicle_1'].selected_trajectory
        if selected_trajectory != self.trajectory_number:
            print("Trajectory has changed")
            self.load_trajectory(selected_trajectory)
            self.controller.update_reference(self._trajectory)
            self.first_time = False


        for agent_settings in carla_interface_settings.agents.values():
            if hasattr(agent_settings, 'selected_controller'):
                if agent_settings.selected_controller == str(self.settings):
                    if 'SensoDrive' in agent_settings.selected_input:
                        stiffness = hardware_manager_shared_variables.inputs[agent_settings.selected_input].auto_center_stiffness
                        steering_angle = hardware_manager_shared_variables.inputs[agent_settings.selected_input].steering_angle

                        # Compose a state containing the car information
                        car_state = np.array([[carlainterface_shared_variables.agents[agent_settings.__str__()].transform[0]],
                                              [carlainterface_shared_variables.agents[agent_settings.__str__()].transform[1]],
                                              [math.radians(carlainterface_shared_variables.agents[agent_settings.__str__()].transform[3])]])

                        car_velocity = np.array([carlainterface_shared_variables.agents[agent_settings.__str__()].velocities_in_world_frame[0],
                                                 carlainterface_shared_variables.agents[agent_settings.__str__()].velocities_in_world_frame[1]])

                        timestep = time_step_in_ns / 1e9  # [s]

                        # Compute control inputs using current position vector
                        self.shared_variables, nonlinear_component, estimated_human_input = self.controller.compute_input(stiffness, steering_angle, timestep,
                                                                                                                                  car_state, car_velocity, self.torque_fdca,
                                                                                                                                  self.shared_variables,
                                                                                                                                  agent_settings.use_intention,
                                                                                                                                  carlainterface_shared_variables.agents[
                                                                                                                                      agent_settings.__str__()])

                        self.torque_fdca = self.shared_variables.req_torque # self._bq_filter_torque.step(self.shared_variables.req_torque)# - nonlinear_component)
                        hardware_manager_shared_variables.inputs[agent_settings.selected_input].torque = self.torque_fdca


class FDCAControllerSettings:
    def __init__(self, identifier=''):
        self.k_y = 0.05
        self.k_psi = 3.0
        self.lohs = 0.85
        self.sohf = 0.5
        self.loha = 0.6
        self.trajectory_name = "hcr_trajectory.csv"
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
    def __init__(self, wheel_base=2.406, effective_ratio=1 / 13, human_compatible_reference=None):
        self.in_disagreement = False
        self.wheel_base = wheel_base
        self.effective_ratio = effective_ratio
        self._trajectory = human_compatible_reference
        self._bq_filter_curve = LowPassFilterBiquad(fc=30, fs=100)
        self._bq_filter_theta = LowPassFilterBiquad(fc=15, fs=100)

        self.torque_sensor = TorqueSensor()
        self.torque = 0.0
        self.timer = 0.0

    def update_reference(self, trajectory):
        self._trajectory = trajectory

    def compute_input(self, stiffness, steering_angle, timestep, car_state, car_velocity, old_torque, shared_variables, intention_aware, carla_interface_shared_variables):
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

        if car_state[0] == 0.0 and car_state[1] == 0.0:
            # set the shared variables
            shared_variables.sw_des = 0.0
            shared_variables.ff_torque = 0.0
            shared_variables.fb_torque = 0.0
            shared_variables.loha_torque = 0.0
            shared_variables.req_torque = 0.0
            shared_variables.lat_error = 0.0
            shared_variables.heading_error = 0.0
            estimated_human_control_input = 0.0
            nonlinear_component = 0.0

        else:
            estimated_human_control_input, nonlinear_component = self.torque_sensor.estimate_human_torque(steering_angle, old_torque, timestep)
            variables_hcr = self._compute_torques(car_state, car_velocity, carla_interface_shared_variables, shared_variables, steering_angle, stiffness, use_current_lane=False)
            variables_lane = self._compute_torques(car_state, car_velocity, carla_interface_shared_variables, shared_variables, steering_angle, stiffness, use_current_lane=True)

            if self.in_disagreement and intention_aware:
                variables = variables_lane
                print("We are disagreeing now!")
                # Follow the lane if necessary
                self.timer += timestep
                if -0.2 < estimated_human_control_input * variables_hcr['torque'] < 0.2 and self.timer > 1.0:
                    self.in_disagreement = False

            else:
                # Else follow hcr
                variables = variables_hcr

            # When detecting a "high" force conflict, follow lane until conflict is dissolved
            if estimated_human_control_input * variables_hcr['torque'] < -0.4:
                self.in_disagreement = True
                self.timer = 0
            shared_variables = self._set_shared_variables(shared_variables, variables)

        return shared_variables, nonlinear_component, estimated_human_control_input

    def _set_shared_variables(self, shared_variables, variables):
        shared_variables.sw_des = (variables['feedforward_torque'] + variables['feedback_torque']) / variables['stiffness']
        shared_variables.ff_torque = variables['feedforward_torque']
        shared_variables.fb_torque = variables['feedback_torque']
        shared_variables.loha_torque = variables['loha_torque']
        shared_variables.req_torque = variables['torque']
        shared_variables.lat_error = variables['error[0]']
        shared_variables.heading_error = variables['error[1]']
        shared_variables.x_road = variables['x_road']
        shared_variables.y_road = variables['y_road']
        return shared_variables

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

    def _compute_torques(self, car_state, car_velocity, carla_interface_shared_variables, shared_variables, steering_angle, stiffness, use_current_lane):
        x_road, y_road, road_state, steering_reference = self._get_references(car_state, car_velocity, carla_interface_shared_variables, use_current_lane)
        error = self._calculate_error(car_state, car_velocity, road_state)
        feedforward_torque = shared_variables.lohs * (stiffness * steering_reference)  # LOHS torque (feedforward)
        feedback_torque = shared_variables.sohf * (shared_variables.k_y * error[0] + shared_variables.k_psi * error[1])  # SOHF torque (feedback)
        loha_torque = shared_variables.loha * ((feedforward_torque + feedback_torque) / stiffness - steering_angle)  # LOHA torque
        fdca_torque = feedforward_torque + feedback_torque + loha_torque
        torque = fdca_torque

        variables = {}
        variables['feedforward_torque'] = feedforward_torque
        variables['feedback_torque'] = feedback_torque
        variables['loha_torque'] = loha_torque
        variables['torque'] = torque
        variables['error[0]'] = error[0]
        variables['error[1]'] = error[1]
        variables['x_road'] = x_road
        variables['y_road'] = y_road
        variables['stiffness'] = stiffness

        return variables

    def _calculate_error(self, car_state, car_velocity, road_state):
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

        # Bug that when speed is very low, the reference steering angle is compute very badly
        velocity_magnitude = math.sqrt(car_velocity[0] ** 2 + car_velocity[1] ** 2)
        if velocity_magnitude < 3:
            error_local_frame[2, 0] = 0

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
                idx.append(len(self._trajectory[:, 0]) - 1)
            elif i < 0:
                idx.append(0)
            else:
                idx.append(i)
        return idx

    def _get_road_state(self, carla_interface_shared_variables):
        x_road = carla_interface_shared_variables.data_road_x
        y_road = carla_interface_shared_variables.data_road_y
        return x_road, y_road

    def _compute_road_properties(self, data, s, history):
        # Cubic interpolation through generated midpoints to generate midline
        smoothing_factor = 0.5
        look_ahead = 10
        tck, _ = cp.interpolate.splprep(data, u=s, s=smoothing_factor)

        dx_dt, dy_dt = cp.interpolate.splev(history + look_ahead, tck, der=1)
        road_heading = self._heading(dx_dt, dy_dt)

        d2x_dt2, d2y_dt2 = cp.interpolate.splev(history + look_ahead, tck, der=2)
        road_curvature = self._curvature(dx_dt, d2x_dt2, dy_dt, d2y_dt2)

        return road_heading, road_curvature

    def _wrong_direction(self, car_velocity, road_heading):
        car_heading = self._heading(car_velocity[0], car_velocity[1])
        heading_difference = road_heading - car_heading
        velocity = math.sqrt(car_velocity[0] ** 2 + car_velocity[1] ** 2)

        if heading_difference > math.pi:
            heading_difference -= 2.0 * math.pi
        if heading_difference < -math.pi:
            heading_difference += 2.0 * math.pi
        if velocity > 2:
            if abs(heading_difference) > 0.5 * math.pi:
                return True
            else:
                return False
        else:
            return False

    def _get_references(self, car_state, car_velocity, carla_interface_shared_variables, use_current_lane):
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
        # Are we getting data from a HCR?
        n = 50  # samples
        history = 25
        s = list(range(n))

        # Just follow the road if at end of trajectory
        end_of_trajectory = False
        if self._trajectory is not None:
            pos_car = [car_state[0, 0], car_state[1, 0]]
            id_now = find_closest_node(pos_car, self._trajectory[:, 1:3])
            if id_now > len(self._trajectory[:, 1]) - history:
                end_of_trajectory = True
                print("reached the end of the trajectory")

        if self._trajectory is not None and not use_current_lane and not end_of_trajectory:
            id = s + id_now - history
            idx = self._check_end(id)
            x_road = self._trajectory[idx, 1]
            y_road = self._trajectory[idx, 2]
        else:
            x_road, y_road = self._get_road_state(carla_interface_shared_variables)

        data = np.array([x_road, y_road])
        road_heading, road_curvature = self._compute_road_properties(data, s, history)
        if self._wrong_direction(car_velocity, road_heading):
            x_road.reverse()
            y_road.reverse()
            data = np.array([x_road, y_road])
            road_heading, road_curvature = self._compute_road_properties(data, s, history)

        if math.isnan(road_curvature):
            road_curvature = 0
            # road_heading = self._heading(car_velocity[0], car_velocity[1])
            print("NaN value detected!!")
        curve_filtered = self._bq_filter_curve.step(road_curvature)
        road_heading_filtered = self._bq_filter_theta.step(road_heading)
        road_state = np.array([[x_road[history]], [y_road[history]], [road_heading_filtered]])
        steering_reference = math.atan(self.wheel_base * curve_filtered) / self.effective_ratio

        return x_road, y_road, road_state, steering_reference



