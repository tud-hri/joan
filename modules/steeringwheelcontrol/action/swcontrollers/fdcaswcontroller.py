import os

import math
import time

from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from .baseswcontroller import BaseSWController
from utils.utils import Biquad
import numpy as np

class FDCASWController(BaseSWController):

    def __init__(self, module_action):
        super().__init__(controller_type=SWContollerTypes.FDCA_SWCONTROLLER, module_action=module_action)

        # Initialize local Variables
        self._hcr_list = []
        self._hcr = []
        self._t_lookahead = 0.0
        self._k_y = 0.1
        self._k_psi = 0.4
        self._lohs = 1.0
        self._sohf = 1.0
        self._loha = 0.0

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

        self._current_trajectory_name = ''
        self.update_trajectory_list()

        # connect widgets
        self._controller_tab.btn_apply.clicked.connect(self.get_set_parameter_values_from_ui)
        self._controller_tab.btn_reset.clicked.connect(self.set_default_parameter_values)
        self._controller_tab.slider_loha.valueChanged.connect(
            lambda: self._controller_tab.lbl_loha.setText(str(self._controller_tab.slider_loha.value()/100.0))
        )
        self._controller_tab.btn_update_hcr_list.clicked.connect(self.update_trajectory_list)

        self.set_default_parameter_values()

    def do(self, data_in, hw_data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""
        if 'SensoDrive 1' in hw_data_in:
            stiffness = hw_data_in['SensoDrive 1']['spring_stiffness']
            sw_angle = hw_data_in['SensoDrive 1']['SteeringInput']
            

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
            
            ############## FDCA SPECIFIC CALCULATIONS HERE ##############
            self._data_out['sw_torque'] = 0
            SWAngle_FB = self._sohf_func(self._k_y, self._k_psi, self._sohf, -self._controller_error[0], self._controller_error[1])
            SWAngle_FFdes = self._feed_forward_controller(0, car)
            SWAngle_FF = self._lohs_func(self._lohs, SWAngle_FFdes)
            SWAngleFB_FFDes = SWAngle_FB + SWAngle_FFdes #in radians
            SWAngle_Current = math.radians(sw_angle)
            delta_SW = SWAngleFB_FFDes - SWAngle_Current
            SWAngle_FF_FB = SWAngle_FF + SWAngle_FB
            Torque_LoHA = self._loha_func(self._loha, delta_SW) #Torque resulting from feedback
            K_stiffnessDeg = stiffness # 40mNm/deg [DEGREES! CONVERT TO RADIANS!!]
            K_stiffnessRad = K_stiffnessDeg  * (math.pi/180)
            #print(K_stiffnessRad, math.radians(K_stiffnessDeg))
            #Torque_FF_FB = self.InverseSteeringDyn(SWAngle_FF_FB,K_stiffness)
            Torque_FF_FB = self._inverse_steering_dyn(SWAngle_FF_FB,K_stiffnessRad)

            Torque_FDCA = Torque_LoHA + Torque_FF_FB
            

            #print(round(Torque_FDCA*1000))
            intTorque = int(round(Torque_FDCA*1000))
            print(self._controller_error[0], math.degrees(self._controller_error[1]), intTorque)
            self._data_out['sw_torque'] =  intTorque
    

            #update variables
            self.error_static_old = error_static
            self._t2 = t1

        else:
            self._data_out['sw_torque'] = 0

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


    def _sohf_func(self, _k_y, _k_psi, _sohf, DeltaY, DeltaPsi):
        Temp = _sohf* (_k_y * DeltaY + _k_psi * DeltaPsi)

        return Temp

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


        SWangle_FFdes = math.radians(self._trajectory[feed_forward_index_plus1, 3]*450)


        return SWangle_FFdes


    def _lohs_func(self,_lohs,SWangle_FFDES):
        SWangle_FF = SWangle_FFDES * _lohs

        return SWangle_FF

    def _loha_func(self, _loha, delta_SW):
        Torque_loha = _loha * delta_SW

        
        return Torque_loha

    def _inverse_steering_dyn(self, SWangle,K_Stiffness):
        Torque = SWangle * 1/(1.0/K_Stiffness)

        return Torque







    def set_default_parameter_values(self):
        """set the default controller parameters
        In the near future, this should be from the controller settings class
        """

        # default values
        self._t_lookahead = 0.0
        self._k_y = 0.1
        self._k_psi = 0.4
        self._lohs = 1.0
        self._sohf = 1.0
        self._loha = 0.25

        self.update_ui()

        self.get_set_parameter_values_from_ui()

        # load the default HCR
        self._current_trajectory_name = 'default_hcr_trajectory.csv'
        self.update_trajectory_list()
        self.load_trajectory()

    def get_set_parameter_values_from_ui(self):
        """update controller parameters from ui"""

        self._k_y = float(self._controller_tab.edit_k_y.text())
        self._k_psi = float(self._controller_tab.edit_k_psi.text())
        self._lohs = float(self._controller_tab.edit_lohs.text())
        self._sohf = float(self._controller_tab.edit_sohf.text())
        self._loha = self._controller_tab.slider_loha.value() / 100

        self.load_trajectory()

        self.update_ui()

    def update_ui(self):
        """update the labels and line edits in the controller_tab with the latest values"""

        self._controller_tab.edit_k_y.setText(str(self._k_y))
        self._controller_tab.edit_k_psi.setText(str(self._k_psi))
        self._controller_tab.edit_lohs.setText(str(self._lohs))
        self._controller_tab.edit_sohf.setText(str(self._sohf))
        self._controller_tab.slider_loha.setValue(self._loha*100)

        # update the current controller settings
        self._controller_tab.lbl_k_y.setText(str(self._k_y))
        self._controller_tab.lbl_k_psi.setText(str(self._k_psi))
        self._controller_tab.lbl_lohs.setText(str(self._lohs))
        self._controller_tab.lbl_sohf.setText(str(self._sohf))

