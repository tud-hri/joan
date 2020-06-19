import numpy as np
import math
import time

from utils.utils import Biquad
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from .baseswcontroller import BaseSWController
from PyQt5 import QtWidgets


class PDSWController(BaseSWController):
    def __init__(self, module_action, controller_list_key):
        super().__init__(controller_type=SWControllerTypes.PD_SWCONTROLLER, module_action=module_action)

        self.module_action = module_action

        # controller list key
        self.controller_list_key = controller_list_key
        # default controller values
        self._t_lookahead = 0.6
        self._k_p = 8
        self._k_d = 1
        self._w_lat = 1
        self._w_heading = 2

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

        self.update_trajectory_list()

        # connect widgets

        self._tuning_tab.btn_apply.clicked.connect(self.get_set_parameter_values_from_ui)
        self._tuning_tab.btn_reset.clicked.connect(self.set_default_parameter_values)
        self._tuning_tab.btn_update_hcr_list.clicked.connect(self.update_trajectory_list)

        self.set_default_parameter_values()

    @property
    def get_controller_list_key(self):
        return self.controller_list_key


    def do(self, data_in, hw_data_in):
        if 'SensoDrive 1' in hw_data_in:
            stiffness = hw_data_in['SensoDrive 1']['spring_stiffness']

            """Perform the controller-specific calculations"""
            #get delta_t (we could also use 'millis' but this is a bit more precise)
            t1 = time.time()
            delta_t = t1 - self._t2

            # extract data
            car = data_in['vehicles'][0].spawned_vehicle
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
            
            #put error through controller to get sw torque out
            self._data_out['sw_torque'] = self.pd_controller(self._controller_error, stiffness)
            self._data_out['lat_error'] = self._controller_error[0]
            self._data_out['heading_error'] = self._controller_error[1]
            self._data_out['lat_error_rate'] = self._controller_error[2]
            self._data_out['heading_error_rate'] = self._controller_error[3]

            #update variables
            self.error_static_old = error_static
            self._t2 = t1

        else:
            self._data_out['sw_torque'] = 0
            self._data_out['lat_error'] = 0
            self._data_out['heading_error'] = 0
            self._data_out['lat_error_rate'] = 0
            self._data_out['heading_error_rate'] = 0

 
        

        

        return self._data_out

    def error(self, pos_car, heading_car, vel_car=np.array([0.0, 0.0, 0.0])):
        """Calculate the controller error"""
        pos_car_future = pos_car + vel_car * self._t_lookahead  # linear extrapolation, should be updated

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

    def pd_controller(self, error, stiffness):
        torque_gain_lateral = self._w_lat * (self._k_p * error[0] + self._k_d* error[2])
        torque_gain_heading = self._w_heading * (self._k_p * error[1] + self._k_d* error[3])

        torque_gain = torque_gain_lateral + torque_gain_heading

        torque = -stiffness * torque_gain

        return int(torque)



    def set_default_parameter_values(self):
        """set the default controller parameters
        In the near future, this should be from the controller settings class
        """

        # default values
        self._t_lookahead = 0.6
        self._k_p = 8
        self._k_d = 1
        self._w_lat = 1
        self._w_heading = 2

        self.update_ui()
        self.get_set_parameter_values_from_ui()

        # load the default HCR
        self._current_trajectory_name = 'default_hcr_trajectory.csv'
        self.update_trajectory_list()
        self.load_trajectory()

    def get_set_parameter_values_from_ui(self):
        """update controller parameters from ui"""
        self._t_lookahead = float(self._tuning_tab.edit_t_ahead.text())
        self._k_p = float(self._tuning_tab.edit_gain_prop.text())
        self._k_d = float(self._tuning_tab.edit_gain_deriv.text())
        self._w_lat = float(self._tuning_tab.edit_weight_lat.text())
        self._w_heading = float(self._tuning_tab.edit_weight_heading.text())

        self.load_trajectory()

        self.update_ui()

    def update_ui(self):
        """update the labels and line edits in the controller_tab with the latest values"""

        self._tuning_tab.edit_gain_prop.setText(str(self._k_p))
        self._tuning_tab.edit_gain_deriv.setText(str(self._k_d))
        self._tuning_tab.edit_weight_lat.setText(str(self._w_lat))
        self._tuning_tab.edit_weight_heading.setText(str(self._w_heading))
        self._tuning_tab.edit_t_ahead.setText(str(self._t_lookahead))

        # update the current controller settings
        self._tuning_tab.lbl_current_gain_prop.setText(str(self._k_p))
        self._tuning_tab.lbl_current_gain_deriv.setText(str(self._k_d))
        self._tuning_tab.lbl_current_weight_lat.setText(str(self._w_lat))
        self._tuning_tab.lbl_current_weight_heading.setText(str(self._w_heading))
        self._tuning_tab.lbl_current_t_lookahead.setText(str(self._t_lookahead))
