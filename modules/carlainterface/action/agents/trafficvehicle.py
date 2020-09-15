import math
import os
import time

import numpy as np
import pandas as pd
from PyQt5 import uic, QtWidgets

from modules.carlainterface.action.carlainterfacesettings import TrafficVehicleSettings
from tools.lowpassfilterbiquad import LowPassFilterBiquad
from .basevehicle import Basevehicle


class TrafficvehicleSettingsDialog(QtWidgets.QDialog):
    """
    Settings Dialog class for the trafficvehicle settings class. This dialog should pop up whenever it is asked by the user or when
    creating the traffic vehicle class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
    """
    def __init__(self, trafficvehicle_settings, parent=None):
        """
        Initializes the class
        :param trafficvehicle_settings:
        :param parent:
        """
        super().__init__(parent)
        self.trafficvehicle_settings = trafficvehicle_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/traffic_vehicle_settings_ui.ui"), self)

        self.button_box_trafficvehicle_settings .button(self.button_box_trafficvehicle_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self._update_variables)
        self._display_values()



    def accept(self):
        """
        Accepts and saves the current settings internally (Closes the dialog)
        :return:
        """
        self.trafficvehicle_settings.velocity = self.spin_velocity.value()
        self.trafficvehicle_settings.selected_car = self.combo_car_type.currentText()
        self.trafficvehicle_settings.selected_spawnpoint = self.spin_spawn_points.value()
        self.trafficvehicle_settings._t_lookahead = float(self.edit_t_ahead.text())
        self.trafficvehicle_settings._k_p = float(self.edit_gain_prop.text())
        self.trafficvehicle_settings._k_d = float(self.edit_gain_deriv.text())
        self.trafficvehicle_settings._w_lat = float(self.edit_weight_lat.text())
        self.trafficvehicle_settings._w_heading = float(self.edit_weight_heading.text())
        self.trafficvehicle_settings.trajectory_name = self.combo_box_traffic_trajectory.itemText(self.combo_box_traffic_trajectory.currentIndex())
        self.trafficvehicle_settings._set_velocity_with_pd = self.check_box_pd_vel.isChecked()

        super().accept()

    def _display_values(self, settings_to_display = None):
        """
        Shows the current settings
        :param settings_to_display:
        :return:
        """
        if not settings_to_display:
            settings_to_display = self.trafficvehicle_settings

        self.lbl_current_t_lookahead.setText(str(settings_to_display._t_lookahead))
        self.lbl_current_gain_prop.setText(str(settings_to_display._k_p))
        self.lbl_current_gain_deriv.setText(str(settings_to_display._k_d))
        self.lbl_current_weight_lat.setText(str(settings_to_display._w_lat))
        self.lbl_current_weight_heading.setText(str(settings_to_display._w_heading))

        self.spin_velocity.setValue(settings_to_display._velocity)
        self.edit_t_ahead.setText(str(settings_to_display._t_lookahead))
        self.edit_gain_prop.setText(str(settings_to_display._k_p))
        self.edit_gain_deriv.setText(str(settings_to_display._k_d))
        self.edit_weight_lat.setText(str(settings_to_display._w_lat))
        self.edit_weight_heading.setText(str(settings_to_display._w_heading))

        idx_car = self.combo_car_type.findText(settings_to_display._selected_car)
        self.combo_car_type.setCurrentIndex(idx_car)

        idx_traj = self.combo_box_traffic_trajectory.findText(settings_to_display._trajectory_name)
        self.combo_box_traffic_trajectory.setCurrentIndex(idx_traj)

        self.spin_spawn_points.setValue(settings_to_display._selected_spawnpoint)
        self.check_box_pd_vel.setChecked(settings_to_display._set_velocity_with_pd)

    def _update_variables(self):
        """
        Saves the current settings internally without closing the settings dialog
        :return:
        """
        self.trafficvehicle_settings.velocity = self.spin_velocity.value()
        self.trafficvehicle_settings.selected_car = self.combo_car_type.currentText()
        self.trafficvehicle_settings.selected_spawnpoint = self.spin_spawn_points.value()
        self.trafficvehicle_settings._t_lookahead = float(self.edit_t_ahead.text())
        self.trafficvehicle_settings._k_p = float(self.edit_gain_prop.text())
        self.trafficvehicle_settings._k_d = float(self.edit_gain_deriv.text())
        self.trafficvehicle_settings._w_lat = float(self.edit_weight_lat.text())
        self.trafficvehicle_settings._w_heading = float(self.edit_weight_heading.text())
        self.trafficvehicle_settings.trajectory_name = self.combo_box_traffic_trajectory.itemText(self.combo_box_traffic_trajectory.currentIndex())
        self.trafficvehicle_settings._set_velocity_with_pd = self.check_box_pd_vel.isChecked()

        self._display_values()

    def _set_default_values(self):
        """
        the default values found in 'Carlainterfacesettings -> TrafficVehicleSettings()
        :return:
        """
        self._display_values(TrafficVehicleSettings())

class TrafficVehicle(Basevehicle):
    """
    This class contains everything you need to make a vehicle follow a predefined route by PD control
    """

    def __init__(self, carlainterface_action, name, nr_spawn_points, tags, settings: TrafficVehicleSettings):
        """
        Initializes the class
        :param carlainterface_action:
        :param name:
        :param nr_spawn_points:
        :param tags:
        :param settings:
        """
        super().__init__(carlainterface_action, name=name)
        self.carlainterface_action = carlainterface_action

        self.settings = settings
        self._bq_filter_heading = LowPassFilterBiquad(fs =1000/self.carlainterface_action.tick_interval_ms, fc = 3)
        self._bq_filter_velocity = LowPassFilterBiquad(fs = 1000/self.carlainterface_action.tick_interval_ms, fc = 3)
        self.module_action = carlainterface_action

        self._t2 = 0

        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self.error_static_old = np.array([0.0, 0.0])

        self._current_trajectory_name = ''
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        self._path_trajectory_directory = os.path.join(path, '../steeringwheelcontrol/action/swcontrollers/trajectories/')


        self.vehicle_tab_widget = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/traffic_vehicle_tab.ui"))
        self.vehicle_tab_widget.group_traffic_agent.setTitle(name)

        self.vehicle_tab_widget.btn_destroy.setEnabled(False)

        self.vehicle_tab_widget.btn_spawn.clicked.connect(self.spawn_car)
        self.vehicle_tab_widget.btn_destroy.clicked.connect(self.destroy_car)
        self.vehicle_tab_widget.btn_remove_traffic_agent.clicked.connect(self.remove_traffic_agent)
        self.vehicle_tab_widget.btn_settings.clicked.connect(self._open_settings_dialog)
        self.vehicle_tab_widget.btn_settings.clicked.connect(self._open_settings_dialog_from_button)

        self.settings_dialog = TrafficvehicleSettingsDialog(self.settings)


        self.update_trajectory_list()

        for item in tags:
            self.settings_dialog.combo_car_type.addItem(item)

        self.settings_dialog.spin_spawn_points.setRange(0, nr_spawn_points - 1)

        self.settings_dialog.combo_box_traffic_trajectory.currentIndexChanged.connect(self.set_trajectory_name)
        self.settings_dialog.btn_apply_parameters.clicked.connect(self.load_trajectory)
        self.settings_dialog.accepted.connect(self.load_trajectory)

        self._open_settings_dialog()


    @property
    def vehicle_tab(self):
        return self.vehicle_tab_widget

    def _open_settings_dialog(self):
        """
        Updates the settings dialog without actually showing it
        :return:
        """
        self.settings_dialog._display_values()

    def _open_settings_dialog_from_button(self):
        """
        Updates the settings dialog and also shows it.
        :return:
        """
        self.settings_dialog._display_values()
        self.settings_dialog.show()

    def remove_traffic_agent(self):
        """
        Removes the traffic agent
        :return:
        """
        self.vehicle_tab.setParent(None)
        self.destroy_car()

        #I dont know what these are?
        # self.module_action.traffic_vehicles.remove_input_device(self)
        # self.module_action.settings.traffic_vehicles.remove_input_device(self.settings)

    def set_trajectory_name(self):
        """
        Sets the current to follow trajectory name
        :return:
        """
        self.settings._trajectory_name = self.settings_dialog.combo_box_traffic_trajectory.itemText(self.settings_dialog.combo_box_traffic_trajectory.currentIndex())

    def load_trajectory(self):
        """
        Loads the trajectory which is in the 'trajectories' folder of the steeringwheelcontrol module. The trajectory
        should at least contain [x position, y position and steeringwheel angle]. The way they are structured now is
        as follows:
        [index,PosX,PosY,SteeringAngle,Throttle,Brake,Psi, Vel]
        :return:
        """
        try:
            tmp = pd.read_csv(os.path.join(self._path_trajectory_directory, self.settings._trajectory_name))
            self._trajectory = tmp.values
            # TODO We might want to do some checks on the trajectory here.
            # self.trajectory_name = fname
        except OSError as err:
                print('Error loading HCR trajectory file: ', err)

    def update_trajectory_list(self):
        """
        Check what trajectory files are present and update the selection list
        :return:
        """

        # get list of csv files in directory
        if not os.path.isdir(self._path_trajectory_directory):
            os.mkdir(self._path_trajectory_directory)
        files = [filename for filename in os.listdir(self._path_trajectory_directory) if filename.endswith('csv')]

        self.settings_dialog.combo_box_traffic_trajectory.clear()
        self.settings_dialog.combo_box_traffic_trajectory.addItems(files)

        idx = self.settings_dialog.combo_box_traffic_trajectory.findText(self.settings._trajectory_name)
        if idx != -1:
            self.settings_dialog.combo_box_traffic_trajectory.setCurrentIndex(idx)

    def find_closest_node(self, node, nodes):
        """
        find the node in the nodes list (trajectory), basically finds which node is closest to a list of nodes
        :param node:
        :param nodes:
        :return:
        """
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_squared = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_squared)

    def do(self):
        """
        This ticks at the interval of the module and will update the traffic vehicles control input appropriately.
        :return:
        """
        try:
            ## STEERING ANGLE ##
            """Perform the controller-specific calculations"""
            # get delta_t (we could also use 'tick_interval_ms' but this is a bit more precise)
            t1 = time.time()
            delta_t = t1 - self._t2

            # extract data
            car = self.spawned_vehicle
            pos_car = np.array([car.get_location().x, car.get_location().y])
            vel_car = np.array([car.get_velocity().x, car.get_velocity().y])
            heading_car = car.get_transform().rotation.yaw


            # find static error and error rate:
            error_static = self.error(pos_car, heading_car, vel_car)
            error_rate = self.error_rates(error_static, self.error_static_old, delta_t)

            # filter the error rate with biquad filter
            error_lateral_rate_filtered = self._bq_filter_velocity.step(error_rate[0])
            error_heading_rate_filtered = self._bq_filter_heading.step(error_rate[1])

            # put errors in 1 variable
            self._controller_error[0:2] = error_static
            self._controller_error[2:] = np.array([error_lateral_rate_filtered, error_heading_rate_filtered])

            # put error through controller to get sw torque out
            self._sw_angle = self.trafficvehicle_steeringPD(self._controller_error)
            self._control.steer = self._sw_angle





            # VELOCITY
            if self.settings._set_velocity_with_pd:
                #Throttle method:
                vel_error = self.settings._velocity - (math.sqrt(car.get_velocity().x**2 + car.get_velocity().y**2 + car.get_velocity().z**2)*3.6)
                vel_error_rate = (math.sqrt(car.get_acceleration().x**2 + car.get_acceleration().y**2 + car.get_acceleration().z**2)*3.6)
                error_velocity = [vel_error, vel_error_rate]

                pd_vel_output = self.trafficvehicle_velocityPD(error_velocity)
                if pd_vel_output < 0:
                    self._control.brake = -pd_vel_output
                    self._control.throttle = 0
                    if pd_vel_output < -1:
                        self._control.brake = 1
                elif pd_vel_output > 0:
                    self._control.throttle = pd_vel_output
                    self._control.brake = 0
                    if pd_vel_output > 1:
                        self._control._throttle = 1
            else:
                # Setting velocity method
                forward_vector = car.get_transform().rotation.get_forward_vector()
                vel_traffic = car.get_velocity()
                vel_traffic = forward_vector * self.settings._velocity / 3.6
                self.spawned_vehicle.set_velocity(vel_traffic)
                self._control.brake = 0
                self._control.throttle = 0




            self.spawned_vehicle.apply_control(self._control)

            # update variables
            self.error_static_old = error_static
            self._t2 = t1
        except Exception as inst:

            print(inst)

    def error(self, pos_car, heading_car, vel_car=np.array([0.0, 0.0, 0.0])):
        """
        Calculates the errors of the car with regards to the trajectory.
        :param pos_car:
        :param heading_car:
        :param vel_car:
        :return:
        """
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
        """
        Calculates the rate of error.
        :param error:
        :param error_old:
        :param delta_t:
        :return:
        """
        heading_error_rate = (error[0] - error_old[0]) / delta_t
        velocity_error_rate = (error[1] - error_old[1]) / delta_t

        return np.array([velocity_error_rate, heading_error_rate])

    def trafficvehicle_steeringPD(self, error):
        """
        Minimizes the steering error by pd control.
        :param error:
        :return: steering angle
        """
        lateral_gain = self.settings._w_lat * (self.settings._k_p * error[0] + self.settings._k_d * error[2])
        heading_gain = self.settings._w_heading * (self.settings._k_p * error[1] + self.settings._k_d* error[3])
        #
        total_gain = lateral_gain+ heading_gain
        sw_angle = total_gain/450

        return -sw_angle
        #
        # return int(torque_gain)

    def trafficvehicle_velocityPD(self, error):
        """
        Tries to minimize velocity error by pd control.
        :param error:
        :return: throttle
        """
        _kp_vel = 50
        _kd_vel = 1
        temp = _kp_vel * error[0] + _kd_vel * error[1]

        output = temp/100

        return output

    def stop_traffic(self):
        """
        Sets all traffic to a halt
        :return:
        """
        try:
            car = self.spawned_vehicle
            forward_vector = car.get_transform().rotation.get_forward_vector()
            vel_traffic = car.get_velocity()
            vel_traffic = forward_vector * 0
            self.spawned_vehicle.set_velocity(vel_traffic)

            self._control.brake = 1
            self._control.throttle = 0
            self.spawned_vehicle.apply_control(self._control)
        except:
            pass
