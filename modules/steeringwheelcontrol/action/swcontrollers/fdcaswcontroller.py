import os

import math
import time

from PyQt5 import QtWidgets, uic

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from modules.steeringwheelcontrol.action.steeringwheelcontrolsettings import FDCAcontrollerSettings
from .baseswcontroller import BaseSWController
from utils.utils import Biquad
import numpy as np


class FDCAcontrollerSettingsDialog(QtWidgets.QDialog):
    def __init__(self, fdca_controller_settings, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.fdca_controller_settings = fdca_controller_settings

        uic.loadUi(self.controller.tuning_ui_file, self)
        self.btnbox_fdca_controller_settings.button(self.btnbox_fdca_controller_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self.slider_loha.valueChanged.connect(self._update_loha_slider_label)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)

        self._display_values()

        self.show()

    def update_parameters(self):
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.loha = self.slider_loha.value() / 100

        self._display_values()

    def _update_loha_slider_label(self):
        self.lbl_loha_slider.setText(str(self.slider_loha.value()/100))
        # Uncomment this if you want to real time change the loha value when you slide the slider:
        if self.checkbox_tuning_loha.isChecked():
            self.fdca_controller_settings.loha = self.slider_loha.value() / 100
            self.lbl_loha.setText(str(self.fdca_controller_settings.loha))

    def accept(self):
        self.fdca_controller_settings.k_y = float(self.edit_k_y.text())
        self.fdca_controller_settings.k_psi = float(self.edit_k_psi.text())
        self.fdca_controller_settings.lohs = float(self.edit_lohs.text())
        self.fdca_controller_settings.sohf = float(self.edit_sohf.text())
        self.fdca_controller_settings.loha = self.slider_loha.value() / 100

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
        self.slider_loha.setValue(settings_to_display.loha * 100)




    def _set_default_values(self):
        self._display_values(FDCAcontrollerSettings())

class FDCASWController(BaseSWController):

    def __init__(self, module_action, controller_list_key, settings):
        super().__init__(controller_type=SWControllerTypes.FDCA_SWCONTROLLER, module_action=module_action)

        self.module_action = module_action

        # controller list key
        self.controller_list_key = controller_list_key
        self.settings = settings

        self._t2 = 0

        self._bq_filter_heading = Biquad()
        self._bq_filter_velocity = Biquad()

        self.stiffness = 1

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
        self.settings_dialog = FDCAcontrollerSettingsDialog(self.settings, SWControllerTypes.FDCA_SWCONTROLLER)

    def initialize(self):
        self.load_trajectory()

    def process(self, vehicle_object, hw_data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""
        if vehicle_object.selected_sw_controller == self.controller_list_key:
                try:
                    stiffness = hw_data_in[vehicle_object.selected_input]['spring_stiffness']
                    sw_angle = hw_data_in[vehicle_object.selected_input]['SteeringInput']


                    """Perform the controller-specific calculations"""
                    #get delta_t (we could also use 'millis' but this is a bit more precise)
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

                    #filter the error rate with biquad filter
                    error_lateral_rate_filtered = self._bq_filter_velocity.process(error_rate[0])
                    error_heading_rate_filtered = self._bq_filter_heading.process(error_rate[1])

                    #put errors in 1 variable
                    self._controller_error[0:2] = error_static
                    self._controller_error[2:] = np.array([error_lateral_rate_filtered, error_heading_rate_filtered])

                    ############## FDCA SPECIFIC CALCULATIONS HERE ##############
                    self._data_out['sw_torque'] = 0
                    sw_angle_fb = self._sohf_func(self.settings.k_y, self.settings.k_psi, self.settings.sohf, -self._controller_error[0], self._controller_error[1])
                    sw_angle_ff_des = self._feed_forward_controller(0, car)
                    sw_angle_ff = self.lohs_func(self.settings.lohs, sw_angle_ff_des)
                    sw_angle_fb_ff_des = sw_angle_fb + sw_angle_ff_des #in radians
                    sw_angle_current = math.radians(sw_angle)
                    delta_sw = sw_angle_fb_ff_des - sw_angle_current
                    sw_angle_ff_fb = sw_angle_ff + sw_angle_fb
                    torque_loha = self._loha_func(self.settings.loha, delta_sw) #Torque resulting from feedback
                    k_stiffness_deg = stiffness # 40mNm/deg [DEGREES! CONVERT TO RADIANS!!]
                    k_stiffness_rad = k_stiffness_deg  * (math.pi/180)
                    torque_ff_fb = self._inverse_steering_dyn(sw_angle_ff_fb, k_stiffness_rad)

                    torque_fdca = torque_loha + torque_ff_fb


                    #print(round(Torque_FDCA*1000))
                    torque_integer = int(round(torque_fdca*1000))
                    print(self._controller_error[0], math.degrees(self._controller_error[1]), torque_integer)
                    self._data_out['sw_torque'] = torque_integer


                    #update variables
                    self.error_static_old = error_static
                    self._t2 = t1

                except Exception as inst:
                    print(inst)
                    self._data_out['sw_torque'] = 0

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
        
        heading_error_rate = (error[0] - error_old[0])/delta_t
        velocity_error_rate = (error[1] - error_old[1])/delta_t

        return np.array([velocity_error_rate, heading_error_rate])


    def _sohf_func(self, _k_y, _k_psi, _sohf, DeltaY, DeltaPsi):
        temp = _sohf* (_k_y * DeltaY + _k_psi * DeltaPsi)

        return temp

    def _feed_forward_controller(self, t_ahead, car):
        car_location = car.get_location()
        car_velocity = car.get_velocity()

        location = np.array([car_location.x, car_location.y])
        velocity = np.array([car_velocity.x, car_velocity.y])
        extra_distance = velocity * t_ahead

        future_location = location + extra_distance

        feed_forward_index = self.find_closest_node(future_location, self._trajectory[:, 1:3])
        if(feed_forward_index >= len(self._trajectory)-20):
            feed_forward_index_plus1 = 0
        else:
            feed_forward_index_plus1 = feed_forward_index + 20


        sw_angle_ff_des = math.radians(self._trajectory[feed_forward_index_plus1, 3]*450)


        return sw_angle_ff_des


    def lohs_func(self, _lohs, sw_angle_ff_des):
        sw_angle_ff = sw_angle_ff_des * _lohs

        return sw_angle_ff

    def _loha_func(self, _loha, delta_sw):
        torque_loha = _loha * delta_sw

        
        return torque_loha

    def _inverse_steering_dyn(self, sw_angle, k_stiffness):
        torque = sw_angle * 1/(1.0/k_stiffness)

        return torque






    #
    # def set_default_parameter_values(self):
    #     """set the default controller parameters
    #     In the near future, this should be from the controller settings class
    #     """
    #
    #     # default values
    #     self._t_lookahead = 0.0
    #     self.k_y = 0.1
    #     self.k_psi = 0.4
    #     self.lohs = 1.0
    #     self.sohf = 1.0
    #     self.loha = 0.25
    #
    #     self.update_ui()
    #
    #     self.get_set_parameter_values_from_ui()
    #
    #     # load the default HCR
    #     self._current_trajectory_name = 'default_hcr_trajectory.csv'
    #     self.update_trajectory_list()
    #     self.load_trajectory()
    #
    # def get_set_parameter_values_from_ui(self):
    #     """update controller parameters from ui"""
    #
    #     self.k_y = float(self._tuning_tab.edit_k_y.text())
    #     self.k_psi = float(self._tuning_tab.edit_k_psi.text())
    #     self.lohs = float(self._tuning_tab.edit_lohs.text())
    #     self.sohf = float(self._tuning_tab.edit_sohf.text())
    #     self.loha = self._tuning_tab.slider_loha.value() / 100
    #
    #     self.load_trajectory()
    #
    #     self.update_ui()
    #
    # def update_ui(self):
    #     """update the labels and line edits in the controller_tab with the latest values"""
    #
    #     self._tuning_tab.edit_k_y.setText(str(self.k_y))
    #     self._tuning_tab.edit_k_psi.setText(str(self.k_psi))
    #     self._tuning_tab.edit_lohs.setText(str(self.lohs))
    #     self._tuning_tab.edit_sohf.setText(str(self.sohf))
    #     self._tuning_tab.slider_loha.setValue(self.loha*100)
    #
    #     # update the current controller settings
    #     self._tuning_tab.lbl_k_y.setText(str(self.k_y))
    #     self._tuning_tab.lbl_k_psi.setText(str(self.k_psi))
    #     self._tuning_tab.lbl_lohs.setText(str(self.lohs))
    #     self._tuning_tab.lbl_sohf.setText(str(self.sohf))
    #
