import numpy as np
import math

from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from .baseswcontroller import BaseSWController


class PDSWController(BaseSWController):

    def __init__(self, module_action):
        super().__init__(controller_type=SWContollerTypes.PD_SWCONTROLLER, module_action=module_action)

        # default controller values
        self._t_lookahead = 0.6
        self._k_p = 8
        self._k_d = 1
        self._w_lat = 1
        self._w_heading = 2

        # controller errors
        # [0]: lateral error
        # [1]: heading error
        # [2]: lateral rate error
        # [3]: heading rate error
        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])

        self.update_trajectory_list()

        # connect widgets
        self._controller_tab.btn_apply.clicked.connect(self.get_set_parameter_values_from_ui)
        self._controller_tab.btn_reset.clicked.connect(self.set_default_parameter_values)
        self._controller_tab.btn_update_hcr_list.clicked.connect(self.update_trajectory_list)

        self.set_default_parameter_values()

    def do(self, data_in):
        """Perform the controller-specific calculations"""

        # extract data
        car = data_in['vehicles'][0].spawned_vehicle
        pos_car = np.array([car.get_location().x, car.get_location().y])
        vel_car = np.array([car.get_velocity().x, car.get_velocity().y])
        heading_car = car.get_transform().rotation.yaw
        heading_rate_car = 0.0

        # find error
        self._controller_error = self.error(pos_car, heading_car, vel_car, heading_rate_car)

        # TODO calculate steering wheel torque

        self._data_out['sw_torque'] = 0.0
        return self._data_out

    def error(self, pos_car, heading_car, vel_car=np.array([0.0, 0.0, 0.0]), heading_rate_car=0.0):
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

        # calculate the lateral position error rate
        error_vel_lat = np.dot(vel_car, vec_pos_future) / np.linalg.norm(vec_pos_future)

        # calculate heading error
        heading_ref = self._trajectory[index_closest_waypoint, 6]

        error_heading = -(math.radians(heading_ref) - math.radians(heading_car))

        # Make sure you dont get jumps (basically unwrap the angle with a threshold of pi radians (180 degrees))
        if error_heading > math.pi:
            error_heading = error_heading - 2.0 * math.pi
        if error_heading < -math.pi:
            error_heading = error_heading + 2.0 * math.pi

        # heading rate error
        error_heading_rate = 0.0

        return np.array([error_pos_lat, error_heading, error_vel_lat, error_heading_rate])

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
        self._t_lookahead = float(self._controller_tab.edit_t_ahead.text())
        self._k_p = float(self._controller_tab.edit_gain_prop.text())
        self._k_d = float(self._controller_tab.edit_gain_deriv.text())
        self._w_lat = float(self._controller_tab.edit_weight_lat.text())
        self._w_heading = float(self._controller_tab.edit_weight_heading.text())

        self.load_trajectory()

        self.update_ui()

    def update_ui(self):
        """update the labels and line edits in the controller_tab with the latest values"""

        self._controller_tab.edit_gain_prop.setText(str(self._k_p))
        self._controller_tab.edit_gain_deriv.setText(str(self._k_d))
        self._controller_tab.edit_weight_lat.setText(str(self._w_lat))
        self._controller_tab.edit_weight_heading.setText(str(self._w_heading))
        self._controller_tab.edit_t_ahead.setText(str(self._t_lookahead))

        # update the current controller settings
        self._controller_tab.lbl_current_gain_prop.setText(str(self._k_p))
        self._controller_tab.lbl_current_gain_deriv.setText(str(self._k_d))
        self._controller_tab.lbl_current_weight_lat.setText(str(self._w_lat))
        self._controller_tab.lbl_current_weight_heading.setText(str(self._w_heading))
        self._controller_tab.lbl_current_t_lookahead.setText(str(self._t_lookahead))
