from .basevehicle import Basevehicle
from PyQt5 import uic
from utils.utils import Biquad
import os
import numpy as np
import time
import pandas as pd
import math

class Trafficvehicle(Basevehicle):
    def __init__(self, agent_manager_action, vehicle_nr, nr_spawn_points, tags):
        "Init traffic vehicle here"

        self._bq_filter_heading = Biquad()
        self._bq_filter_velocity = Biquad()
        self.module_action = agent_manager_action

        self._t2 = 0

        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self.error_static_old = np.array([0.0, 0.0])

        self._current_trajectory_name = ''
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        self._path_trajectory_directory = os.path.join(path, '../steeringwheelcontrol/action/swcontrollers/trajectories/')

        self.vehicle_nr = vehicle_nr
        self._vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../trafficvehicletab.ui"))
        self._vehicle_tab.group_traffic_agent.setTitle('Traffic Vehicle ' + str(vehicle_nr + 1))

        self._vehicle_tab.btn_spawn.clicked.connect(self.spawn_car)
        self._vehicle_tab.btn_destroy.clicked.connect(self.destroy_car)
        self._vehicle_tab.btn_remove_traffic_agent.clicked.connect(self.remove_traffic_agent)

        self._vehicle_tab.btn_update_hcr_list.clicked.connect(self.update_trajectory_list)
        self._vehicle_tab.combo_box_traffic_trajectory.currentIndexChanged.connect(self.load_trajectory)

        self._vehicle_tab.spin_spawn_points.setRange(0, nr_spawn_points)
        self._vehicle_tab.spin_spawn_points.lineEdit().setReadOnly(True)

        self.update_trajectory_list()

        # DIT MOET NOG IN DE SETTINGS
        self.w_lat = 1
        self.w_heading = 2
        self.k_p = 6
        self.k_d = 2.5


        for item in tags:
            self._vehicle_tab.combo_car_type.addItem(item)


    @property
    def vehicle_tab(self):
        return self._vehicle_tab

    def remove_traffic_agent(self):
        self._vehicle_tab.setParent(None)
        self.destroy_car()

        self.module_action.traffic_vehicles.remove(self)

    def load_trajectory(self):
        """Load HCR trajectory"""
        fname = self._vehicle_tab.combo_box_traffic_trajectory.itemText(self._vehicle_tab.combo_box_traffic_trajectory.currentIndex())

        if fname != self._current_trajectory_name:
            # fname is different from _current_hcr_name, load it!
            try:
                tmp = pd.read_csv(os.path.join(self._path_trajectory_directory, fname))
                self._trajectory = tmp.values
                # TODO We might want to do some checks on the trajectory here.
                self._current_trajectory_name = fname
            except OSError as err:
                print('Error loading HCR trajectory file: ', err)

    def update_trajectory_list(self):
        """Check what trajectory files are present and update the selection list"""
        # get list of csv files in directory
        if not os.path.isdir(self._path_trajectory_directory):
            os.mkdir(self._path_trajectory_directory)
        files = [filename for filename in os.listdir(self._path_trajectory_directory) if filename.endswith('csv')]

        self._vehicle_tab.combo_box_traffic_trajectory.clear()
        self._vehicle_tab.combo_box_traffic_trajectory.addItems(files)

        idx = self._vehicle_tab.combo_box_traffic_trajectory.findText(self._current_trajectory_name)
        if idx != -1:
            self._vehicle_tab.combo_box_traffic_trajectory.setCurrentIndex(idx)

    def find_closest_node(self, node, nodes):
        """find the node in the nodes list (trajectory)"""
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_squared = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_squared)

    def process(self):
        try:
            """Perform the controller-specific calculations"""
            # get delta_t (we could also use 'millis' but this is a bit more precise)
            t1 = time.time()
            delta_t = t1 - self._t2

            # extract data
            car = self.spawned_vehicle
            pos_car = np.array([car.get_location().x, car.get_location().y])
            vel_car = np.array([car.get_velocity().x, car.get_velocity().y])
            heading_car = car.get_transform().rotation.yaw
            forward_vector = car.get_transform().rotation.get_forward_vector()
            # vel_traffic = car.get_velocity()
            vel_traffic = forward_vector * 60/3.6

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
            self._sw_angle = self.pd_controller(self._controller_error)
            print(self._sw_angle)
            self._control.steer = self._sw_angle
            self.spawned_vehicle.apply_control(self._control)
            self.spawned_vehicle.set_velocity(vel_traffic)


            # update variables
            self.error_static_old = error_static
            self._t2 = t1
        except Exception as inst:

            print(inst)

    def error(self, pos_car, heading_car, vel_car=np.array([0.0, 0.0, 0.0])):
        """Calculate the controller error"""
        pos_car_future = pos_car + vel_car * 0.6  # linear extrapolation, should be updated


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

    def pd_controller(self, error):
        lateral_gain = self.w_lat * (self.k_p * error[0] + self.k_d * error[2])
        heading_gain = self.w_heading * (self.k_p * error[1] + self.k_d* error[3])
        #
        total_gain = lateral_gain+ heading_gain
        sw_angle = total_gain/450

        return -sw_angle
        #
        # return int(torque_gain)

    def stop_traffic(self):
        try:
            car = self.spawned_vehicle
            forward_vector = car.get_transform().rotation.get_forward_vector()
            # vel_traffic = car.get_velocity()
            vel_traffic = forward_vector *0
            self.spawned_vehicle.set_velocity(vel_traffic)
        except:
            pass
