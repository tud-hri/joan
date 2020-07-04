import math
import time

import numpy as np
from PyQt5 import QtWidgets, uic

from modules.steeringwheelcontrol.action.steeringwheelcontrolsettings import PDcontrollerSettings
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from utils.utils import Biquad
from .baseswcontroller import BaseSWController


class PDcontrollerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, pd_controller_settings, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.pd_controller_settings = pd_controller_settings

        uic.loadUi(self.controller.tuning_ui_file, self)
        self.btnbox_pd_controller_settings.button(self.btnbox_pd_controller_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)

        self._display_values()

        self.show()

    def update_parameters(self):
        self.pd_controller_settings.t_lookahead = float(self.edit_t_ahead.text())
        self.pd_controller_settings.k_p = float(self.edit_gain_prop.text())
        self.pd_controller_settings.k_d = float(self.edit_gain_deriv.text())
        self.pd_controller_settings.w_lat = float(self.edit_weight_lat.text())
        self.pd_controller_settings.w_heading = float(self.edit_weight_heading.text())

        self._display_values()

    def accept(self):
        self.pd_controller_settings.t_lookahead = float(self.edit_t_ahead.text())
        self.pd_controller_settings.k_p = float(self.edit_gain_prop.text())
        self.pd_controller_settings.k_d = float(self.edit_gain_deriv.text())
        self.pd_controller_settings.w_lat = float(self.edit_weight_lat.text())
        self.pd_controller_settings.w_heading = float(self.edit_weight_heading.text())

        super().accept()

    def _display_values(self, settings_to_display=None):
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

    def _set_default_values(self):
        self._display_values(PDcontrollerSettings())


class PDSWController(BaseSWController):
    def __init__(self, module_action, controller_list_key, settings):
        super().__init__(controller_type=SWControllerTypes.PD_SWCONTROLLER, module_action=module_action)

        self.module_action = module_action
        self.settings = settings
        # controller list key
        self.controller_list_key = controller_list_key

        self.current_reference_trajectory = []

        # Variables to make differential control possible (need to declare second timevariable before use)
        self._t2 = 0

        # Setting up filters
        self._bq_filter_heading = Biquad()
        self._bq_filter_velocity = Biquad()

        # controller errors
        # [0]: lateral error
        # [1]: heading error
        # [2]: lateral rate error
        # [3]: heading rate error
        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self.error_static_old = np.array([0.0, 0.0])

        # Get the target trajectory name from settings
        self.selected_reference_trajectory = []

        # self.set_default_parameter_values()
        self._open_settings_dialog()

        self._controller_tab.btn_settings_sw_controller.clicked.connect(self._open_settings_dialog)
        self._controller_tab.btn_update_hcr_list.clicked.connect(self.update_trajectory_list)

        # immediately load the correct HCR after index change
        self._controller_tab.cmbbox_hcr_selection.currentIndexChanged.connect(self.load_trajectory)

    @property
    def get_controller_list_key(self):
        return self.controller_list_key

    def _open_settings_dialog(self):
        self.settings_dialog = PDcontrollerSettingsDialog(self.settings, SWControllerTypes.PD_SWCONTROLLER)

    def initialize(self):
        self.load_trajectory()

    def process(self, vehicle_object, hw_data_in):
        try:
            stiffness = hw_data_in[vehicle_object.selected_input]['spring_stiffness']
        except:
            stiffness = 1
        if vehicle_object.selected_sw_controller == self.controller_list_key:
            try:
                """Perform the controller-specific calculations"""
                # get delta_t (we could also use 'millis' but this is a bit more precise)
                t1 = time.time()
                delta_t = t1 - self._t2

                # extract data
                car = vehicle_object.spawned_vehicle
                pos_car = np.array([car.get_location().x, car.get_location().y])
                vel_car = np.array([car.get_velocity().x, car.get_velocity().y])
                heading_car = car.get_transform().rotation.yaw

                # find static error and error rate:
                error_static = self.error(pos_car, heading_car, vel_car)
                error_rate = self.error_rates(error_static, self.error_static_old, delta_t)

                # filter the error rate with biquad filter
                error_lateral_rate_filtered = self._bq_filter_velocity.process(error_rate[0])
                error_heading_rate_filtered = self._bq_filter_heading.process(error_rate[1])

                # put errors in 1 variable
                self._controller_error[0:2] = error_static
                self._controller_error[2:] = np.array([error_lateral_rate_filtered, error_heading_rate_filtered])

                # put error through controller to get sw torque out
                self._data_out['sw_torque'] = self.pd_controller(self._controller_error, stiffness)

                # update variables
                self.error_static_old = error_static
                self._t2 = t1
            except Exception as inst:
                self._data_out['sw_torque'] = 0
                print(inst)

            return self._data_out
        else:
            self._data_out['sw_torque'] = 0
            return self._data_out

    def error(self, pos_car, heading_car, vel_car=np.array([0.0, 0.0, 0.0])):
        """Calculate the controller error"""
        pos_car_future = pos_car + vel_car * self.settings.t_lookahead  # linear extrapolation, should be updated

        # Find waypoint index of the point that the car would be in the future (compared to own driven trajectory)
        index_closest_waypoint = self.find_closest_node(pos_car_future, self._trajectory[:, 1:3])

        if index_closest_waypoint >= len(self._trajectory) - 3:
            index_closest_waypoint_next = 0
        else:
            index_closest_waypoint_next = index_closest_waypoint + 3

        # calculate lateral error
        pos_ref_future = self._trajectory[index_closest_waypoint, 1:3]
        pos_ref_future_next = self._trajectory[index_closest_waypoint_next, 1:3]

        vec_pos_future = pos_car_future - pos_ref_future
        vec_dir_future = pos_ref_future_next - pos_ref_future

        error_lat_sign = np.math.atan2(np.linalg.det([vec_dir_future, vec_pos_future]),
                                       np.dot(vec_dir_future, vec_pos_future))

        error_pos_lat = np.sqrt(vec_pos_future.dot(vec_pos_future))

        if error_lat_sign < 0:
            error_pos_lat = -error_pos_lat

        # calculate heading error
        heading_ref = self._trajectory[index_closest_waypoint, 6]

        error_heading = -(math.radians(heading_ref) - math.radians(heading_car))

        # Make sure you dont get jumps (basically unwrap the angle with a threshold of pi radians (180 degrees))
        if error_heading > math.pi:
            error_heading = error_heading - 2.0 * math.pi
        if error_heading < -math.pi:
            error_heading = error_heading + 2.0 * math.pi

        return np.array([error_pos_lat, error_heading])

    def error_rates(self, error, error_old, delta_t):
        """Calculate the controller error rates"""

        heading_error_rate = (error[0] - error_old[0]) / delta_t
        velocity_error_rate = (error[1] - error_old[1]) / delta_t

        return np.array([velocity_error_rate, heading_error_rate])

    def pd_controller(self, error, stiffness):
        torque_gain_lateral = self.settings.w_lat * (self.settings.k_p * error[0] + self.settings.k_d * error[2])
        torque_gain_heading = self.settings.w_heading * (self.settings.k_p * error[1] + self.settings.k_d * error[3])

        torque_gain = torque_gain_lateral + torque_gain_heading

        torque = -stiffness * torque_gain

        return int(torque)
