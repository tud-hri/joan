import math

import numpy as np
from PyQt5 import QtWidgets, uic

from modules.steeringwheelcontrol.action.steeringwheelcontrolsettings import FDCAControllerSettings
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from tools import LowPassFilterBiquad
from .baseswcontroller import BaseSWController, find_closest_node


class FDCAControllerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, fdca_controller_settings, controller, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.fdca_controller_settings = fdca_controller_settings

        uic.loadUi(self.controller.tuning_ui_file, self)
        self.btnbox_fdca_controller_settings.button(
            self.btnbox_fdca_controller_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self.slider_loha.valueChanged.connect(self._update_loha_slider_label)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)

        #hardcode lookahead time if someone needs it
        self.t_lookahead = 0

        self._loha_resolution = 50
        self.slider_loha.setMaximum(self._loha_resolution)
        self.spin_loha.setMaximum(self._loha_resolution)

        self._display_values()


    def update_parameters(self):
        self.slider_loha.setValue(self.spin_loha.value())
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.loha = float(self.slider_loha.value())
        self.fdca_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        self._display_values()

    def _update_loha_slider_label(self):
        self.spin_loha.setValue(self.slider_loha.value())
        if self.checkbox_tuning_loha.isChecked():
            self.fdca_controller_settings.loha = float(self.slider_loha.value())
            self.lbl_loha.setText(str(self.fdca_controller_settings.loha))


    def accept(self):
        self.slider_loha.setValue(self.spin_loha.value())
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.loha = float(self.slider_loha.value())
        self.fdca_controller_settings.trajectory_name = self.cmbbox_hcr_selection.itemText(
            self.cmbbox_hcr_selection.currentIndex())

        super().accept()

    def _display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.fdca_controller_settings

        # update the current controller settings
        self.lbl_k_y.setText(str(settings_to_display.k_y))
        self.lbl_k_psi.setText(str(settings_to_display.k_psi))
        self.lbl_lohs.setText(str(settings_to_display.lohs))
        self.lbl_sohf.setText(str(settings_to_display.sohf))
        self.lbl_loha.setText(str(settings_to_display.loha))

        self.edit_k_y.setText(str(settings_to_display.k_y))
        self.edit_k_psi.setText(str(settings_to_display.k_psi))
        self.edit_lohs.setText(str(settings_to_display.lohs))
        self.edit_sohf.setText(str(settings_to_display.sohf))
        self.slider_loha.setValue(settings_to_display.loha)
        self.spin_loha.setValue(settings_to_display.loha)

        idx_traj = self.cmbbox_hcr_selection.findText(settings_to_display.trajectory_name)
        self.cmbbox_hcr_selection.setCurrentIndex(idx_traj)

    def _set_default_values(self):
        self._display_values(FDCAControllerSettings())
        self.update_parameters()


class FDCASWController(BaseSWController):

    def __init__(self, module_action, controller_list_key, settings):
        super().__init__(controller_type=SWControllerTypes.FDCA_SWCONTROLLER, module_action=module_action)

        self.module_action = module_action

        # controller list key
        self.controller_list_key = controller_list_key
        self.settings = settings

        self._t2 = 0

        self._bq_filter_heading = LowPassFilterBiquad(fc=30, fs=1000 / self.module_action._millis)
        self._bq_filter_velocity = LowPassFilterBiquad(fc=30, fs=1000 / self.module_action._millis)

        self.stiffness = 1

        # hardcode lookahead time if someone needs it
        self.t_lookahead = 0

        # controller errors
        # [0]: lateral error
        # [1]: heading error
        # [2]: lateral rate error
        # [3]: heading rate error
        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self._error_old = np.array([0.0, 0.0])

        # Get the target trajectory name from settings
        self.selected_reference_trajectory = []

        # immediately load the correct HCR after index change

        self.settings_dialog = FDCAControllerSettingsDialog(self.settings, SWControllerTypes.FDCA_SWCONTROLLER)

        self._controller_tab.btn_settings_sw_controller.clicked.connect(self._open_settings_dialog_from_button)

        self.settings_dialog.btn_apply_parameters.clicked.connect(self.load_trajectory)
        self.settings_dialog.accepted.connect(self.load_trajectory)

        self.settings_dialog.btnbox_fdca_controller_settings.button(
            self.settings_dialog.btnbox_fdca_controller_settings.RestoreDefaults).clicked.connect(
            self.load_trajectory)

        self._open_settings_dialog()

    @property
    def get_controller_list_key(self):
        return self.controller_list_key

    def _open_settings_dialog(self):
        self.load_trajectory()
        self.settings_dialog._display_values()

    def _open_settings_dialog_from_button(self):
        self.settings_dialog._display_values()
        self.settings_dialog.show()

    def initialize(self):
        self.load_trajectory()

    def calculate(self, vehicle_object, hw_data_in):
        """
        In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero
        :param vehicle_object:
        :param hw_data_in:
        :return:
        """
        if vehicle_object.selected_sw_controller == self.controller_list_key:
            try:
                # make sure this is in [Nm/rad]
                try:
                    stiffness = hw_data_in[vehicle_object.selected_input]['spring_stiffness']
                except:
                    stiffness = 1
                sw_angle = hw_data_in[vehicle_object.selected_input]['steering_angle']  # [rad]

                # get delta_t (we could also use 'tick_interval_ms' but this is a bit more precise)
                delta_t = self.module_action.tick_interval_ms / 1000  # [s]
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

                # extract data
                car = vehicle_object.spawned_vehicle
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

                # FDCA specific calculations here
                # strength of haptic feedback
                sw_angle_fb = self.settings.sohf * (self.settings.k_y * self._controller_error[0] + self.settings.k_psi * self._controller_error[1])

                # get feedforward sw angle
                sw_angle_ff_des = self._get_reference_sw_angle(self.t_lookahead, car)

                # level of haptic support (feedforward); get sw angle needed for haptic support
                sw_angle_ff = self.settings.lohs * sw_angle_ff_des

                # calculate torques

                # loha torque
                # calculate sw error; BASED ON BASTIAAN PETERMEIJER's SIMULINK IMPLEMENTATION OF THE FDCA
                # add fb and ff sw angles to get total desired sw angle; this is the sw angle the sw should get
                delta_sw = (sw_angle_fb + sw_angle_ff_des) - sw_angle

                torque_loha = delta_sw * self.settings.loha  # loha should be [Nm/rad]

                # feedforward/feedback torque
                sw_angle_ff_fb = sw_angle_ff + sw_angle_fb

                # simplified inverse steering dynamics

                # check: the inherent SW stiffness should not be zero (div by 0)
                if abs(stiffness) < (1 ** -6):
                    stiffness = np.sign(stiffness) * (1 ** -6)

                torque_ff_fb = sw_angle_ff_fb * 1.0  / (1.0 / stiffness)  # !!! stiffness should be in [Nm/rad]

                # total torque of FDCA, to be sent to SW controller in Nm
                torque_fdca = torque_loha + torque_ff_fb

                # print("torque_fdca = {}, torque_ff_fb = {}, torque_loha = {}, sw_angle_des = {}, sw_angle = {}".format(torque_fdca, torque_ff_fb, torque_loha, sw_angle_ff_des, sw_angle))
                # print("sw_angle = {}, sw_angle_fb = {}, sw_angle_ff = {}, ".format(sw_angle, sw_angle_fb, sw_angle_ff))


                # print(torque_integer)
                self._data_out['sw_torque'] = torque_fdca  # [Nm]
                #self._data_out['sw_torque'] = 0

                # update variables
                self._error_old = error
                self._data_out['sw_angle_desired_radians'] = sw_angle_ff_des + sw_angle_fb
                self._data_out['sw_angle_current_radians'] = sw_angle
                self._data_out['lat_error'] = error[0]
                self._data_out['heading_error'] = error[1]
                self._data_out['delta_t'] = delta_t
                self._data_out['lat_error_rate_unfiltered'] = error_rate[0]
                self._data_out['heading_error_rate_unfiltered'] = error_rate[1]
                self._data_out['lat_error_rate_filtered'] = error_rate_filtered[0]
                self._data_out['heading_error_rate_filtered'] = error_rate_filtered[1]
                self._data_out['k_psi'] = self.settings.k_psi
                self._data_out['k_y'] = self.settings.k_y
                self._data_out['sohf'] = self.settings.sohf
                self._data_out['loha'] = self.settings.loha
                self._data_out['lohs'] = self.settings.lohs
                self._data_out['delta_sw'] = delta_sw


                # self._data_out['sw_angle_desired_degrees'] = math.degrees(sw_angle_ff_des)


                return self._data_out

            except Exception as inst:
                print(inst)
                self._data_out['sw_torque'] = 0.0
                self._data_out['sw_angle_desired_radians'] = 0
                return self._data_out
        else:
            self._data_out['sw_torque'] = 0.0
            self._data_out['sw_angle_desired_radians'] = 0

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
        pos_car = pos_car + vel_car * self.t_lookahead  # linear extrapolation, should be updated

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

    def _get_reference_sw_angle(self, t_ahead, car):
        car_location = car.get_location()
        car_velocity = car.get_velocity()

        location = np.array([car_location.x, car_location.y])
        velocity = np.array([car_velocity.x, car_velocity.y])

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
