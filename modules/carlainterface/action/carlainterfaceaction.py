from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QApplication

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State
from process.status import Status
from utils.utils import Biquad

import time
import random
import os
import sys
import glob
import pandas as pd
import numpy as np
import math

msg_box = QMessageBox()
msg_box.setTextFormat(QtCore.Qt.RichText)

try:
    sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    import carla  

except IndexError:
    msg_box.setText("""
                <h3> Could not find the carla python API! </h3>
                <h3> Check whether you copied the egg file correctly, reference:
            <a href=\"https://joan.readthedocs.io/en/latest/setup-run-joan/#getting-necessary-python3-libraries-to-run-joan\">https://joan.readthedocs.io/en/latest/setup-run-joan/#getting-necessary-python3-libraries-to-run-joan</a>
            </h3>
            """)
    msg_box.exec()
    pass

class CarlainterfaceAction(JoanModuleAction):
    def __init__(self, millis=5):
        super().__init__(module=JOANModules.CARLA_INTERFACE, millis=millis)

        #Initialize Variables
        self.data = {}
        self.data['agents'] = {}
        self.data['connected'] = False
        self.write_news(news=self.data)
        self.time = QtCore.QTime()
        self._data_from_hardware = {}

        #Carla connection variables:
        self.host = 'localhost'
        self.port = 2000
        self.connected = False
        self.vehicle_tags = []
        self.vehicles = []
        self.traffic_vehicles = []

        #initialize modulewide state handler
        self.status = Status()

        self._available_controllers = []

        self.hardware_manager_state_machine = self.status.get_module_state_machine(JOANModules.HARDWARE_MANAGER)
        self.hardware_manager_state_machine.add_state_change_listener(self._hardware_state_change_listener)
        self._hardware_state_change_listener()

        self.sw_controller_state_machine = self.status.get_module_state_machine(JOANModules.STEERING_WHEEL_CONTROL)
        self.sw_controller_state_machine.add_state_change_listener(self._sw_controller_state_change_listener)
        self._sw_controller_state_change_listener()
        #print(self.hardware_manager_state_machine.current_state)

        #message box for error display
        self.msg = QMessageBox()

        ## State handling (these are for now all the same however maybe in the future you want to add other functionality)
        self.state_machine.set_transition_condition(State.IDLE, State.READY, self._init_condition)
        self.state_machine.set_transition_condition(State.READY, State.RUNNING, self._starting_condition)
        self.state_machine.set_transition_condition(State.RUNNING, State.READY, self._stopping_condition)

    @property 
    def vehicle_bp_library(self):
        return self._vehicle_bp_library

    @property 
    def world(self):
        return self._world
    
    @property 
    def spawnpoints(self):
        return self._spawn_points

    def _hardware_state_change_listener(self):
        " This function is linked to the state change of the hardware manager and updates the state whenever it changes"

        self.hardware_manager_state = self.status.get_module_current_state(JOANModules.HARDWARE_MANAGER)
        if self.hardware_manager_state is not State.RUNNING:
            for vehicle in self.vehicles:
                vehicle.get_available_inputs()

    def _sw_controller_state_change_listener(self):
        """This function is linked to the state change of the sw_controller, if new controllers are initialized they will be
        automatically added to a variable which contains the options in the SW controller combobox"""
        self.sw_controller_state = self.status.get_module_current_state(JOANModules.STEERING_WHEEL_CONTROL)

        if self.sw_controller_state is not State.RUNNING:
            for vehicle in self.vehicles:
                    vehicle.get_available_controllers()



    def _starting_condition(self):
        try:
            if self.connected is True:

                return True, ''
            else:
                return False, 'Carla is not connected!'
        except KeyError:
            return False, 'Could not check whether carla is connected'


    def _init_condition(self):
        try:
            if self.connected is True:
                # TODO: move this example to the new enum
                return True, ''
            else:
                return False, 'Carla is not connected'
        except KeyError:
            return False, 'Could not check whether carla is connected'

    def _stopping_condition(self):
        try:
            if self.connected is True:
                # TODO: move this example to the new enum
                return True, ''
            else:
                return False, 'Carla is not connected'
        except KeyError:
            return False, 'Could not check whether carla is connected'

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        if self.connected:
            # self.data['vehicles'] = self.vehicles
            for agent in self.vehicles:
                self.data['agents'][agent.vehicle_nr] = agent.unpack_vehicle_data()
            self.write_news(news=self.data)
            self._data_from_hardware = self.read_news(JOANModules.HARDWARE_MANAGER)
            try:
                for items in self.vehicles:
                    if items.spawned:
                        items.apply_control(self._data_from_hardware)
                for items in self.traffic_vehicles:
                    if items.spawned:
                        items.process()
            except Exception as inst:
                print('Could not apply control', inst)
        else:
            self.stop()

    def check_connection(self):
        return self.connected

    def connect(self):
        """
        This function will try and connect to carla server if it is running in unreal
        If not a message box will pop up and the module will transition to error state.
        """
        if not self.connected:
            try:
                print(' connecting')
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.client = carla.Client(self.host, self.port)  # connecting to server
                self.client.set_timeout(2.0)
                time.sleep(2)
                self._world = self.client.get_world()  # get world object (contains everything)
                blueprint_library = self.world.get_blueprint_library()
                self._vehicle_bp_library = blueprint_library.filter('vehicle.*')
                for items in self.vehicle_bp_library:
                    self.vehicle_tags.append(items.id[8:])
                world_map = self._world.get_map()
                self._spawn_points = world_map.get_spawn_points()
                self.nr_spawn_points = len(self._spawn_points)
                print('JOAN connected to CARLA Server!')
                QApplication.restoreOverrideCursor()

                self.connected = True
            except RuntimeError as inst:
                QApplication.restoreOverrideCursor()
                self.msg.setText('Could not connect check if CARLA is running in Unreal')
                self.msg.exec()
                self.connected = False
                QApplication.restoreOverrideCursor()

            self.data['connected'] = self.connected
            self.write_news(news=self.data)

        else:
            self.msg.setText('Already Connected')
            self.msg.exec()

        return self.connected

    def disconnect(self):
        """
        This function will try and disconnect from the carla server, if the module was running it will transition into
        an error state
        """
        if self.connected:
            print('Disconnecting')
            for cars in self.vehicles:
                cars.destroy_car()

            self.client = None
            self._world = None
            self.connected = False
            self.data['connected'] = self.connected
            self.write_news(news=self.data)

            self.state_machine.request_state_change(State.IDLE, 'Carla Disconnected')

        return self.connected

    def add_ego_agent(self):
        self.vehicles.append(Carlavehicle(self, len(self.vehicles), self.nr_spawn_points, self.vehicle_tags))
        for vehicle in self.vehicles:
            vehicle.get_available_inputs()
            vehicle.get_available_controllers()

        " only make controller available for first car for now"
        for vehicle in self.vehicles[1:]:
            vehicle.vehicle_tab.combo_sw_controller.setEnabled(False)

        return self.vehicles

    def add_traffic_agent(self):
        self.traffic_vehicles.append(Trafficvehicle(self, len(self.traffic_vehicles), self.nr_spawn_points, self.vehicle_tags))


        return self.traffic_vehicles

    def initialize(self):
        """
        This function is called before the module is started
        """
        if 'carla' not in sys.modules.keys():
            self.state_machine.request_state_change(State.ERROR, "carla module is NOT imported, make sure the API is available and restart the program")

        if self.state_machine.current_state is State.IDLE:

            self.connect()
            self.state_machine.request_state_change(State.READY, "You can now add vehicles and start module")
        elif self.state_machine.current_state is State.ERROR and 'carla' in sys.modules.keys():
           self.state_machine.request_state_change(State.IDLE)
        return super().initialize()

    def start(self):
        try:
            self.state_machine.request_state_change(State.RUNNING,"Carla interface Running")
            self.time.restart()
            return super().start()

        except RuntimeError:
            return False


    def stop(self):
        try:
            for vehicle in self.vehicles:
                vehicle.get_available_inputs()
                vehicle.get_available_controllers()
            self.state_machine.request_state_change(State.READY, "You can now add vehicles and start the module")

            for traffic in self.traffic_vehicles:
                traffic.stop_traffic()
        except RuntimeError:
            return False
        return super().stop()
        

class Carlavehicle():
    def __init__(self, CarlainterfaceAction, carnr, nr_spawn_points, tags):
        self.carnr = carnr
        self.module_action = CarlainterfaceAction
        self._vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "vehicletab.ui"))
        self._vehicle_tab.group_car.setTitle('Car ' + str(carnr+1))
        self._spawned = False
        self._hardware_data = {}
        self._sw_controller_data = {}
        self._vehicle_nr = 'Car ' + str(carnr+1)
        self._sw_controller = self._vehicle_tab.combo_sw_controller.currentText()

        self.car_data = {}

        self._vehicle_tab.spin_spawn_points.setRange(0, nr_spawn_points)
        self._vehicle_tab.spin_spawn_points.lineEdit().setReadOnly(True)
        self._vehicle_tab.btn_destroy.setEnabled(False)
        self._vehicle_tab.combo_input.currentTextChanged.connect(self.update_input)
        self._vehicle_tab.combo_sw_controller.currentTextChanged.connect(self.update_sw_controller)

        self._vehicle_tab.btn_spawn.clicked.connect(self.spawn_car)
        self._vehicle_tab.btn_destroy.clicked.connect(self.destroy_car)
        self._vehicle_tab.btn_remove_ego_agent.clicked.connect(self.remove_ego_agent)

        for item in tags:
            self._vehicle_tab.comboCartype.addItem(item)

        self._selected_input = str('None')

    @property
    def vehicle_tab(self):
        return self._vehicle_tab

    @property
    def spawned(self):
        return self._spawned

    @property
    def selected_input(self):
        return self._selected_input

    @property
    def selected_sw_controller(self):
        return self._sw_controller

    @property
    def vehicle_id(self):
        return self._BP.id

    @property
    def vehicle_nr(self):
        return self._vehicle_nr

    def update_sw_controller(self):
        self._sw_controller = self._vehicle_tab.combo_sw_controller.currentText()

    def update_input(self):
        self._selected_input = self._vehicle_tab.combo_input.currentText()

    def get_available_inputs(self):
        self._vehicle_tab.combo_input.clear()
        self._vehicle_tab.combo_input.addItem('None')
        self._hardware_data = self.module_action.read_news(JOANModules.HARDWARE_MANAGER)
        for keys in self._hardware_data:
            self._vehicle_tab.combo_input.addItem(str(keys))

    def get_available_controllers(self):
        self._vehicle_tab.combo_sw_controller.clear()
        self._vehicle_tab.combo_sw_controller.addItem('None')
        self._sw_controller_data = self.module_action.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        for keys in self._sw_controller_data:
            self._vehicle_tab.combo_sw_controller.addItem(str(keys))

    def unpack_vehicle_data(self):
        try:
            #spatial:
            self.car_data['x_pos'] = self.spawned_vehicle.get_transform().location.x
            self.car_data['y_pos'] = self.spawned_vehicle.get_transform().location.y
            self.car_data['z_pos'] = self.spawned_vehicle.get_transform().location.z
            self.car_data['yaw'] = self.spawned_vehicle.get_transform().rotation.yaw
            self.car_data['pitch'] = self.spawned_vehicle.get_transform().rotation.pitch
            self.car_data['roll'] = self.spawned_vehicle.get_transform().rotation.roll
            self.car_data['x_ang_vel'] = self.spawned_vehicle.get_angular_velocity().x
            self.car_data['y_ang_vel'] = self.spawned_vehicle.get_angular_velocity().y
            self.car_data['z_ang_vel'] = self.spawned_vehicle.get_angular_velocity().z
            self.car_data['x_vel'] = self.spawned_vehicle.get_velocity().x
            self.car_data['y_vel'] = self.spawned_vehicle.get_velocity().y
            self.car_data['z_vel'] = self.spawned_vehicle.get_velocity().z
            self.car_data['x_acc'] = self.spawned_vehicle.get_acceleration().x
            self.car_data['y_acc'] = self.spawned_vehicle.get_acceleration().y
            self.car_data['z_acc'] = self.spawned_vehicle.get_acceleration().z
            self.car_data['forward_vector_x_component'] = self.spawned_vehicle.get_transform().rotation.get_forward_vector().x
            self.car_data['forward_vector_y_component'] = self.spawned_vehicle.get_transform().rotation.get_forward_vector().y
            self.car_data['forward_vector_z_component'] = self.spawned_vehicle.get_transform().rotation.get_forward_vector().z


            #inputs
            last_applied_vehicle_control = self.spawned_vehicle.get_control()
            self.car_data['throttle_input'] = last_applied_vehicle_control.throttle
            self.car_data['brake_input'] = last_applied_vehicle_control.brake
            self.car_data['steering_input'] = last_applied_vehicle_control.steer
            self.car_data['reverse'] = last_applied_vehicle_control.reverse
            self.car_data['manual_gear_shift'] = last_applied_vehicle_control.manual_gear_shift
            self.car_data['gear'] = last_applied_vehicle_control.gear

        except:
            pass




        return self.car_data


    def destroy_inputs(self):
        self._vehicle_tab.combo_input.clear()
        self._vehicle_tab.combo_input.addItem('None')


    def spawn_car(self):
        self._BP = random.choice(self.module_action.vehicle_bp_library.filter("vehicle." + str(self._vehicle_tab.comboCartype.currentText())))
        self._control = carla.VehicleControl()
        try:
            spawnpointnr = self._vehicle_tab.spin_spawn_points.value()-1
            self.spawned_vehicle = self.module_action.world.spawn_actor(self._BP, self.module_action.spawnpoints[spawnpointnr])
            self._vehicle_tab.btn_spawn.setEnabled(False)
            self._vehicle_tab.btn_destroy.setEnabled(True)
            self._vehicle_tab.spin_spawn_points.setEnabled(False)
            self._vehicle_tab.comboCartype.setEnabled(False)
            #self.get_available_inputs()
            self._spawned = True
        except Exception as inst:
            print('Could not spawn car:', inst)
            self._vehicle_tab.btn_spawn.setEnabled(True)
            self._vehicle_tab.btn_destroy.setEnabled(False)
            self._vehicle_tab.spin_spawn_points.setEnabled(True)
            self._vehicle_tab.comboCartype.setEnabled(True)
            self._spawned = False

    def destroy_car(self):
        try:
            self._spawned = False
            self.spawned_vehicle.destroy()
            self._vehicle_tab.btn_spawn.setEnabled(True)
            self._vehicle_tab.btn_destroy.setEnabled(False)
            self._vehicle_tab.spin_spawn_points.setEnabled(True)
            self._vehicle_tab.comboCartype.setEnabled(True)
        except Exception as inst:
            self._spawned = True
            print('Could not destroy spawn car:', inst)
            self._vehicle_tab.btn_spawn.setEnabled(False)
            self._vehicle_tab.btn_destroy.setEnabled(True)
            self._vehicle_tab.spin_spawn_points.setEnabled(False)
            self._vehicle_tab.comboCartype.setEnabled(False)

    def apply_control(self, data):
        if self._selected_input != 'None':
            self._control.steer = data[self._selected_input]['SteeringInput'] / 450
            self._control.throttle = data[self._selected_input]['ThrottleInput'] / 100
            self._control.brake = data[self._selected_input]['BrakeInput'] / 100
            self._control.reverse = data[self._selected_input]['Reverse']
            self._control.hand_brake = data[self._selected_input]['Handbrake']
            self.spawned_vehicle.apply_control(self._control)

    def remove_ego_agent(self):
        self._vehicle_tab.setParent(None)
        self.destroy_car()

        self.module_action.vehicles.remove(self)

class Trafficvehicle():
    def __init__(self, CarlainterfaceAction, traffic_vehicle_nr, nr_spawn_points, tags):
        "Init traffic vehicle here"

        self._bq_filter_heading = Biquad()
        self._bq_filter_velocity = Biquad()

        self._t2 = 0

        self._controller_error = np.array([0.0, 0.0, 0.0, 0.0])
        self.error_static_old = np.array([0.0, 0.0])

        self._current_trajectory_name = ''
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        self._path_trajectory_directory = os.path.join(path, 'steeringwheelcontrol/action/swcontrollers/trajectories/')

        self.traffic_vehicle_nr = traffic_vehicle_nr
        self.module_action = CarlainterfaceAction
        self._traffic_vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "trafficvehicletab.ui"))
        self._traffic_vehicle_tab.group_traffic_agent.setTitle('Traffic Vehicle ' + str(traffic_vehicle_nr + 1))

        self._traffic_vehicle_tab.btn_spawn.clicked.connect(self.spawn_car)
        self._traffic_vehicle_tab.btn_destroy.clicked.connect(self.destroy_car)
        self._traffic_vehicle_tab.btn_remove_traffic_agent.clicked.connect(self.remove_traffic_agent)

        self._traffic_vehicle_tab.btn_update_hcr_list.clicked.connect(self.update_trajectory_list)
        self._traffic_vehicle_tab.combo_box_traffic_trajectory.currentIndexChanged.connect(self.load_trajectory)

        self._traffic_vehicle_tab.spin_spawn_points.setRange(0, nr_spawn_points)
        self._traffic_vehicle_tab.spin_spawn_points.lineEdit().setReadOnly(True)

        self.update_trajectory_list()

        self.w_lat = 1
        self.w_heading = 2
        self.k_p = 6
        self.k_d = 2.5


        for item in tags:
            self._traffic_vehicle_tab.combo_car_type.addItem(item)


    @property
    def traffic_vehicle_tab(self):
        return self._traffic_vehicle_tab

    @property
    def spawned(self):
        return self._spawned

    @property
    def vehicle_id(self):
        return self._BP.id


    def spawn_car(self):
        self._BP = random.choice(self.module_action.vehicle_bp_library.filter("vehicle." + str(self.traffic_vehicle_tab.combo_car_type.currentText())))
        self._traffic_control = carla.VehicleControl()
        try:
            spawnpointnr = self._traffic_vehicle_tab.spin_spawn_points.value()-1
            self.spawned_traffic_vehicle = self.module_action.world.spawn_actor(self._BP, self.module_action.spawnpoints[spawnpointnr])
            self._traffic_vehicle_tab.btn_spawn.setEnabled(False)
            self._traffic_vehicle_tab.btn_destroy.setEnabled(True)
            self._traffic_vehicle_tab.spin_spawn_points.setEnabled(False)
            self._traffic_vehicle_tab.combo_car_type.setEnabled(False)
            self.traffic_velocity = self.spawned_traffic_vehicle.get_velocity()
            #self.get_available_inputs()
            self._spawned = True
        except Exception as inst:
            print('Could not spawn car:', inst)
            self._traffic_vehicle_tab.btn_spawn.setEnabled(True)
            self._traffic_vehicle_tab.btn_destroy.setEnabled(False)
            self._traffic_vehicle_tab.spin_spawn_points.setEnabled(True)
            self._traffic_vehicle_tab.combo_car_type.setEnabled(True)
            self._spawned = False

    def destroy_car(self):
        try:
            self._spawned = False
            self.spawned_traffic_vehicle.destroy()
            self._traffic_vehicle_tab.btn_spawn.setEnabled(True)
            self._traffic_vehicle_tab.btn_destroy.setEnabled(False)
            self._traffic_vehicle_tab.spin_spawn_points.setEnabled(True)
            self._traffic_vehicle_tab.combo_car_type.setEnabled(True)
        except Exception as inst:
            self._spawned = True
            print('Could not destroy spawn car:', inst)
            self._traffic_vehicle_tab.btn_spawn.setEnabled(False)
            self._traffic_vehicle_tab.btn_destroy.setEnabled(True)
            self._traffic_vehicle_tab.spin_spawn_points.setEnabled(False)
            self._traffic_vehicle_tab.combo_car_type.setEnabled(False)

    def remove_traffic_agent(self):
        self._traffic_vehicle_tab.setParent(None)
        self.destroy_car()

        self.module_action.traffic_vehicles.remove(self)

    def load_trajectory(self):
        """Load HCR trajectory"""
        fname = self._traffic_vehicle_tab.combo_box_traffic_trajectory.itemText(self._traffic_vehicle_tab.combo_box_traffic_trajectory.currentIndex())

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

        self._traffic_vehicle_tab.combo_box_traffic_trajectory.clear()
        self._traffic_vehicle_tab.combo_box_traffic_trajectory.addItems(files)

        idx = self._traffic_vehicle_tab.combo_box_traffic_trajectory.findText(self._current_trajectory_name)
        if idx != -1:
            self._traffic_vehicle_tab.combo_box_traffic_trajectory.setCurrentIndex(idx)

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
            car = self.spawned_traffic_vehicle
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
            self._traffic_control.steer = self._sw_angle
            self.spawned_traffic_vehicle.apply_control(self._traffic_control)
            self.spawned_traffic_vehicle.set_velocity(vel_traffic)


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
        car = self.spawned_traffic_vehicle
        forward_vector = car.get_transform().rotation.get_forward_vector()
        # vel_traffic = car.get_velocity()
        vel_traffic = forward_vector *0
        self.spawned_traffic_vehicle.set_velocity(vel_traffic)
