from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QApplication

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State

import time
import random
import os
import sys
import glob

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
    #def __init__(self, master_state_handler, millis=5):
        super().__init__(module=JOANModules.CARLA_INTERFACE, millis=millis)

        #Initialize Variables
        self.data = {}
        self.data['vehicles'] = None
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

    def _starting_condition(self):
        try:
            if self.connected is True:
                # TODO: move this example to the new enum
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
            self.data['vehicles'] = self.vehicles
            self.write_news(news=self.data)
            self._data_from_hardware = self.read_news(JOANModules.HARDWARE_MANAGER)
            try:
                for items in self.vehicles:
                    if items.spawned:
                        items.apply_control(self._data_from_hardware)
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

    def update_cars(self, value):
        #Delete excess vehicles if any
        while value < len(self.vehicles):
            self.vehicles.pop(-1)

        # Create new vehicles:
        for carnr in range(len(self.vehicles), value):
            self.vehicles.append(Carlavehicle(self, carnr, self.nr_spawn_points, self.vehicle_tags))

        return self.vehicles

    def initialize(self):
        """
        This function is called before the module is started
        """
        if(self.state_machine.current_state is State.IDLE):

            self.connect()
            self.state_machine.request_state_change(State.READY, "You can now start the module")
        elif (self.state_machine.current_state is State.ERROR):
            self.state_machine.request_state_change(State.IDLE)
        return super().initialize()

    def start(self):
        try:
            self.state_machine.request_state_change(State.RUNNING,"Carla interface Running")
            self.time.restart()
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.state_machine.request_state_change(State.READY, "Carla interface Stopped")
        except RuntimeError:
            return False
        return super().stop()
        

class Carlavehicle():
    def __init__(self, CarlainterfaceAction, carnr, nr_spawn_points, tags):
        self.module_action = CarlainterfaceAction
        self._vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "vehicletab.ui"))
        self._vehicle_tab.group_car.setTitle('Car ' + str(carnr+1))
        self._spawned = False
        self._hardware_data = {}
        self._vehicle_nr = 'Car ' + str(carnr+1)

        self._vehicle_tab.spin_spawn_points.setRange(0, nr_spawn_points)
        self._vehicle_tab.spin_spawn_points.lineEdit().setReadOnly(True)
        self._vehicle_tab.btn_destroy.setEnabled(False)
        self._vehicle_tab.combo_input.currentTextChanged.connect(self.update_input)

        self._vehicle_tab.btn_spawn.clicked.connect(self.spawn_car)
        self._vehicle_tab.btn_destroy.clicked.connect(self.destroy_car)
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
    def vehicle_id(self):
        return self._BP.id

    @property
    def vehicle_nr(self):
        return self._vehicle_nr


    def update_input(self):
        self._selected_input = self._vehicle_tab.combo_input.currentText()

    def get_available_inputs(self):
        self._hardware_data = self.module_action.read_news(JOANModules.HARDWARE_MANAGER)
        for keys in self._hardware_data:
            self._vehicle_tab.combo_input.addItem(str(keys))
        

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
            self.get_available_inputs()
            self._spawned = True
        except Exception as inst:
            print('Could not spawn car:', inst)
            self._vehicle_tab.btn_spawn.setEnabled(True)
            self._vehicle_tab.btn_destroy.setEnabled(False)
            self._vehicle_tab.spin_spawn_points.setEnabled(True)
            self._spawned = False

    def destroy_car(self):
        try:
            self._spawned = False
            self.spawned_vehicle.destroy()
            self._vehicle_tab.btn_spawn.setEnabled(True)
            self._vehicle_tab.btn_destroy.setEnabled(False)
            self._vehicle_tab.spin_spawn_points.setEnabled(True)
            self.destroy_inputs()
        except Exception as inst:
            self._spawned = True
            print('Could not destroy spawn car:', inst)
            self._vehicle_tab.btn_spawn.setEnabled(False)
            self._vehicle_tab.btn_destroy.setEnabled(True)
            self._vehicle_tab.spin_spawn_points.setEnabled(False)

    def apply_control(self, data):
        if self._selected_input != 'None':
            self._control.steer = data[self._selected_input]['SteeringInput'] / 450
            self._control.throttle = data[self._selected_input]['ThrottleInput'] / 100
            self._control.brake = data[self._selected_input]['BrakeInput'] / 100
            self._control.reverse = data[self._selected_input]['Reverse']
            self._control.hand_brake = data[self._selected_input]['Handbrake']
            self.spawned_vehicle.apply_control(self._control)
