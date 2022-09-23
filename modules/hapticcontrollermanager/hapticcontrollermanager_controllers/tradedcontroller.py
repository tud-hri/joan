import math
import os

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic

from core.statesenum import State
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes
from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAController
from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.torque_sensor import TorqueSensor
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
        self.trajectory_number = 0
        self.load_trajectory()

        # TODO: get wheelbase and keff from car
        self.controller = FDCAController(wheel_base=2.406, effective_ratio=1 / 13, human_compatible_reference=self._trajectory)
        self.torque_sensor = TorqueSensor()

        # filtering
        self.frequency = 100
        self._bq_filter_velocity = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_heading = LowPassFilterBiquad(fc=25, fs=self.frequency)
        self._bq_filter_rate = LowPassFilterBiquad(fc=25, fs=self.frequency)
        # self._bq_filter_torque = LowPassFilterBiquad(fc=5, fs=100)

        # Controller states

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
        self.time = 0.0
        self.torque_tc = 0.0

        self.first_time = True


        # Takeover requests
        self.takeover_requests = True

        # threshold to check if a trajectory is circular in meters; subsequent points need to be 1 m of each other
        self.threshold_circular_trajectory = 1.0

    def load_trajectory(self):
        """Load HCR trajectory"""
        print("loading HCR trajectory")
        if self.carla_interface_settings.agents["Ego Vehicle_1"].random_trajectory:
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

    def do(self, time_step_in_ns, carlainterface_shared_variables, hardware_manager_shared_variables, carla_interface_settings):
        """
        :param time_step_in_ns:
        :param carlainterface_shared_variables:
        :param hardware_manager_shared_variables:
        :param carla_interface_settings:
        :return:
        """

        for agent_settings in carla_interface_settings.agents.values():
            if hasattr(agent_settings, 'selected_controller'):
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

                        car_velocity = np.array([carlainterface_shared_variables.agents[agent_settings.__str__()].velocities_in_world_frame[0],
                                                carlainterface_shared_variables.agents[agent_settings.__str__()].velocities_in_world_frame[1]])

                        # Compute control inputs using current position vector
                        self.shared_variables, nonlinear_component, estimated_human_input = self.controller.compute_input(self.stiffness, steering_angle, delta_t,
                                                                                                                                       car_state, car_velocity, self.torque_tc,
                                                                                                                                       self.shared_variables, agent_settings.use_intention,
                                                                                                                                       carlainterface_shared_variables.agents[agent_settings.__str__()])
                        # print(estimated_human_input)
                        self.torque_tc = self.compute_tc(self.shared_variables.req_torque, delta_t, estimated_human_input) - nonlinear_component
                        # self.torque_tc = - nonlinear_component
                        hardware_manager_shared_variables.inputs[agent_settings.selected_input].torque = self.torque_tc

                        # Check for takeover requests
                        # self.check_takeover_request(car_state, carla_interface_settings, carlainterface_shared_variables, car_name="audi.a2")

                        # Set the shared variables


    def compute_tc(self, torque_fdca, timestep, estimated_human_control_input):
        """
        inputs
            torque_fdca (float): torque computed using the FDCA controller which yields a stable trajectory
            steering_angle (float): Steering angle of the SensoDrive
            timestep (float): Time since last computations

        outputs
            torque (float): output steering torque, with nonlinear component compensation
        """
        authority = self._compute_authority(delta_t=timestep, estimated_human_torque=estimated_human_control_input)
        torque = torque_fdca * authority
        max_torque = 2.5
        self.torque = max(min(torque, max_torque), -max_torque)
        return self.torque

    def _compute_authority(self, delta_t, estimated_human_torque):
        # See if the threshold is crossed and if so increase authority
        if estimated_human_torque ** 2 > self.torque_threshold ** 2:
            direction = -2  # Decrease authority
        else:
            direction = 2  # Increase authority
        self.x_ += delta_t * direction * self.shared_variables.gamma
        self.x_ = min(max(self.x_, -0.5), 3.5)
        c1 = 3
        c2 = 0.5
        authority = 1 - (1 + math.exp(-c1 * (self.x_ - c2))) ** -1
        authority = min(max(authority, 0), 1)
        print(authority)
        return authority

class TradedControllerSettings:
    def __init__(self, identifier=''):
        self.k_y = 0.03
        self.k_psi = 2.5
        self.lohs = 1.0
        self.sohf = 1.0
        self.loha = 1.0
        self.alpha = 0.1
        self.tau_th = 0.2
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

