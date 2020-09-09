import math
import time

import numpy as np
from PyQt5 import QtWidgets, uic

from modules.steeringwheelcontrol.action.steeringwheelcontrolsettings import PDControllerSettings
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from tools import LowPassFilterBiquad
from .baseswcontroller import BaseSWController, find_closest_node


class PDControllerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, pd_controller_settings, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.pd_controller_settings = pd_controller_settings

        uic.loadUi(self.controller.tuning_ui_file, self)
        self.btnbox_pd_controller_settings.button(self.btnbox_pd_controller_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)

    def update_parameters(self):
        self.pd_controller_settings.t_lookahead = float(self.edit_t_ahead.text())
        self.pd_controller_settings.k_p = float(self.edit_gain_prop.text())
        self.pd_controller_settings.k_d = float(self.edit_gain_deriv.text())
        self.pd_controller_settings.w_lat = float(self.edit_weight_lat.text())
        self.pd_controller_settings.w_heading = float(self.edit_weight_heading.text())
        self.pd_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        self.display_values()

    def accept(self):
        self.pd_controller_settings.t_lookahead = float(self.edit_t_ahead.text())
        self.pd_controller_settings.k_p = float(self.edit_gain_prop.text())
        self.pd_controller_settings.k_d = float(self.edit_gain_deriv.text())
        self.pd_controller_settings.w_lat = float(self.edit_weight_lat.text())
        self.pd_controller_settings.w_heading = float(self.edit_weight_heading.text())
        self.pd_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        super().accept()

    def display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.pd_controller_settings

        self.lbl_current_t_lookahead.setText(str(settings_to_display.t_lookahead))
        self.lbl_current_gain_prop.setText(str(settings_to_display.k_p))
        self.lbl_current_gain_deriv.setText(str(settings_to_display.k_d))
        self.lbl_current_weight_lat.setText(str(settings_to_display.w_lat))
        self.lbl_current_weight_heading.setText(str(settings_to_display.w_heading))

        self.edit_t_ahead.setText(str(settings_to_display.t_lookahead))
        self.edit_gain_prop.setText(str(settings_to_display.k_p))
        self.edit_gain_deriv.setText(str(settings_to_display.k_d))
        self.edit_weight_lat.setText(str(settings_to_display.w_lat))
        self.edit_weight_heading.setText(str(settings_to_display.w_heading))

        idx_traj = self.cmbbox_hcr_selection.findText(settings_to_display.trajectory_name)
        self.cmbbox_hcr_selection.setCurrentIndex(idx_traj)

    def _set_default_values(self):
        self.display_values(PDControllerSettings())
        self.update_parameters()


class PDSWController(BaseSWController):
    def __init__(self, module_action, controller_list_key, settings):
        super().__init__(controller_type=SWControllerTypes.PD_SWCONTROLLER, module_action=module_action)

        self.module_action = module_action
        self.settings = settings
        # controller list key
        self.controller_list_key = controller_list_key

        self.current_reference_trajectory = []

        # Variables to make differential control possible (need to declare second timevariable before use)
        self._time_previous_tick = time.time_ns() / (10 ** 9)  # time in nanosecond

        # Setting up filters
        self._bq_filter_heading = LowPassFilterBiquad(fc=10, fs=1000 / self.module_action.tick_interval_ms)
        self._bq_filter_velocity = LowPassFilterBiquad(fc=10, fs=1000 / self.module_action.tick_interval_ms)

        # controller errors
        # [0]: lateral error
        # [1]: heading error
        # [2]: lateral rate error
        # [3]: heading rate error
        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self._error_old = np.array([0.0, 0.0])

        # Get the target trajectory name from settings
        self.selected_reference_trajectory = []

        # self.set_default_parameter_values()

        self._controller_tab.btn_settings_sw_controller.clicked.connect(self._open_settings_dialog_from_button)

        # self._controller_tab.btn_update_hcr_list.clicked.connect(self.update_trajectory_list)

        # immediately load the correct HCR after index change

        self.settings_dialog = PDControllerSettingsDialog(self.settings, SWControllerTypes.PD_SWCONTROLLER)

        self.settings_dialog.btn_apply_parameters.clicked.connect(self.load_trajectory)
        self.settings_dialog.accepted.connect(self.load_trajectory)
        self.settings_dialog.btnbox_pd_controller_settings.button(
            self.settings_dialog.btnbox_pd_controller_settings.RestoreDefaults).clicked.connect(
            self.load_trajectory)

        # self.settings_dialog.cmbbox_hcr_selection.currentIndexChanged.connect(self.load_trajectory)

        self._open_settings_dialog()

    @property
    def get_controller_list_key(self):
        return self.controller_list_key

    def _open_settings_dialog(self):
        self.load_trajectory()
        self.settings_dialog.display_values()

    def _open_settings_dialog_from_button(self):
        # self.load_trajectory()
        self.settings_dialog.display_values()
        self.settings_dialog.show()

    def initialize(self):
        self.load_trajectory()

    def calculate(self, vehicle_object, hw_data_in):
        try:
            stiffness = hw_data_in[vehicle_object.selected_input]['spring_stiffness']
        except:
            stiffness = 1

        if vehicle_object.selected_sw_controller == self.controller_list_key:
            try:
                """Perform the controller-specific calculations"""
                # get delta_t (we could also use 'tick_interval_ms' but this is a bit more precise)
                delta_t = self.module_action.tick_interval_ms
                # _time_this_tick = time.time_ns() / (10 ** 9)  # time in seconds
                # delta_t = _time_this_tick - self._time_previous_tick
                # if delta_t < (self.module_action.tick_interval_ms - 0.5) / 1000:
                #     delta_t = self.module_action.tick_interval_ms / 1000

                # extract data from CARLA
                # CARLA coordinate system (left-handed coordinate system)
                # X: forward
                # Y: right
                # Z: upward
                # Psi (heading): left-hand z-axis positive (yaw to the right is positive)
                # torque: rightward rotation is positive

                car = vehicle_object.spawned_vehicle

                # keep is 2D for now
                pos_car = np.array([car.get_location().x, car.get_location().y])
                vel_car = np.array([car.get_velocity().x, car.get_velocity().y])
                heading_car = car.get_transform().rotation.yaw

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

                # put error through controller to get sw torque out
                self._data_out['sw_torque'] = self.pd_controller(self._controller_error, stiffness)
                self._data_out['lat_error'] = error[0]
                self._data_out['heading_error'] = error[1]
                self._data_out['lat_error_rate_unfiltered'] = error_rate[0]
                self._data_out['heading_error_rate_unfiltered'] = error_rate[1]
                self._data_out['lat_error_rate_filtered'] = error_rate_filtered[0]
                self._data_out['heading_error_rate_filtered'] = error_rate_filtered[1]

                # update variables
                self._error_old = error
                # self._time_previous_tick = _time_this_tick
            except Exception as inst:
                self._data_out['sw_torque'] = 0
                print(inst)

            return self._data_out

        else:
            self._data_out['sw_torque'] = 0
            return self._data_out

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
        pos_car = pos_car + vel_car * self.settings.t_lookahead  # linear extrapolation, should be updated

        # Find waypoint index of the point that the car would be in the future (compared to own driven trajectory)
        index_closest_waypoint = find_closest_node(pos_car, self._trajectory[:, 1:3])

        # TODO: this needs checking
        # circular: if end of the trajectory, go back to the first one; note that this is risky, if the reference trajectory is not circular!
        if index_closest_waypoint >= len(self._trajectory) - 3:
            index_closest_waypoint_next = 0
        else:
            index_closest_waypoint_next = index_closest_waypoint + 3

        # calculate lateral error
        pos_ref = self._trajectory[index_closest_waypoint, 1:3]
        pos_ref_next = self._trajectory[index_closest_waypoint_next, 1:3]

        vec_car = pos_car - pos_ref
        vec_dir = pos_ref_next - pos_ref

        # find the lateral error. Project vec_car on the reference trajectory direction vector
        vec_error_lat = vec_car - (np.dot(vec_car, vec_dir) / np.dot(vec_dir, vec_dir)) * vec_dir
        error_lat = np.sqrt(np.dot(vec_error_lat, vec_error_lat))

        # calculate sign of error using the cross product
        e_sign = np.cross(vec_dir, vec_car)  # used to be e_sign = np.math.atan2(np.linalg.det([vec_dir, vec_car]), np.dot(vec_dir, vec_car))
        e_sign = e_sign / np.abs(e_sign)
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

    def pd_controller(self, error, stiffness):
        """
        Calculate torque for sensodrive
        torque sensordrive: positive clockwise
        CARLA coordinate system:
        X: forward
        Y: right
        Z: upward
        Psi (heading): left-hand z-axis positive (yaw to the right is positive)

        signs lateral error: if the car is to the right of the reference trajectory, sign_lat_error = -1
        sign heading error: if the car is pointing to the right w.r.t. the reference heading, the sign_heading_error = -1
        In both -1 signs, the torque also needs to be negative (e.g. steer to the left).
        :param error:
        :param stiffness:
        :return:
        """
        torque_error_lateral = self.settings.k_p_lat * error[0] + self.settings.k_d_lat * error[2]
        torque_error_heading = self.settings.k_p_heading * error[1] + self.settings.k_d_heading * error[3]

        return torque_error_lateral + torque_error_heading

