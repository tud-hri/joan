from PyQt5 import QtCore, QtWidgets, uic

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import CarlainterfaceStates

import time
import random
import os
import sys
import glob

try:
    sys.path.append(glob.glob('../../carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    import carla  # Hier heb ik dus de PC voor nodig error is onzin!

except IndexError:
    pass

class CarlainterfaceAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=100):
        super().__init__(module=JOANModules.CARLA_INTERFACE, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(CarlainterfaceStates.SIMULATION.INITIALIZING)

        self.data['vehicles'] = {}
        self.write_news(news=self.data)
        self.time = QtCore.QTime()

        #Carla connection variables:
        self.host = 'localhost'
        self.port = 2000
        self.connected = False
        self.vehicle_tags = []
        self.vehicles = []
        # self._vehicle_bp_library = None
        # self._world_map = None
        # self._spawnpoints = None

    @property 
    def vehicle_bp_library(self):
        return self._vehicle_bp_library

    @property 
    def world(self):
        return self._world
    
    @property 
    def spawnpoints(self):
        return self._spawn_points

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        self.write_news(self.data)

    def connect(self):
        try:
            print(' connecting')
            client = carla.Client(self.host, self.port)  # connecting to server
            client.set_timeout(2.0)
            time.sleep(2)
            self._world = client.get_world()  # get world object (contains everything)
            blueprint_library = self.world.get_blueprint_library()
            self._vehicle_bp_library = blueprint_library.filter('vehicle.*')
            for items in self.vehicle_bp_library:
                self.vehicle_tags.append(items.id[8:])
            world_map = self._world.get_map()
            self._spawn_points = world_map.get_spawn_points()
            self.nr_spawn_points = len(self._spawn_points)
            print('JOAN connected to CARLA Server!')

            self.connected = True
        except RuntimeError as inst:
            print('Could not connect error given:', inst)
            self.connected = False

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
        pass

    def start(self):
        try:
            self.module_state_handler.request_state_change(CarlainterfaceStates.SIMULATION.RUNNING)
            self.time.restart()
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(CarlainterfaceStates.SIMULATION.STOPPED)
        except RuntimeError:
            return False
        return super().start()
        

class Carlavehicle():
    def __init__(self, CarlainterfaceAction, carnr, nr_spawn_points, tags):
        #self._parentWidget = Carlainterfacedialog
        self.module_action = CarlainterfaceAction
        self._vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "vehicletab.ui"))
        #self._parentWidget.widget.layOut.addWidget(self._vehicle_tab)
        self._vehicle_tab.group_car.setTitle('Car ' + str(carnr+1))
        self._spawned = False
        self._hardware_data = {}

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

    def update_input(self):
        self._selected_input = self._vehicle_tab.combo_input.currentText()
        print(self._selected_input)

    def get_available_inputs(self):
        self._hardware_data = self.module_action.read_news('modules.hardwaremanager.widget.hardwaremanager.HardwaremanagerWidget')
        for keys in self._hardware_data:
            self._vehicle_tab.combo_input.addItem(str(keys))

    def destroy_inputs(self):
        self._vehicle_tab.combo_input.clear()
        self._vehicle_tab.combo_input.addItem('None')

    def destroy_tab(self):
        self.destroy_car()
        self._spawned = False
        self._parentWidget.widget.layOut.removeWidget(self._vehicle_tab)
        self._vehicle_tab.setParent(None)

    def spawn_car(self):
        self._BP = random.choice(self.module_action.vehicle_bp_library)
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

    def get_vehicle_id(self):
        return self._BP.id

    def apply_control(self, data):
        if self._selected_input != 'None':
            self._control.steer = data[self._selected_input]['SteeringInput'] / 450
            self._control.throttle = data[self._selected_input]['ThrottleInput'] / 100
            self._control.brake = data[self._selected_input]['BrakeInput'] / 100
            self._control.reverse = data[self._selected_input]['Reverse']
            self._control.hand_brake = data[self._selected_input]['Handbrake']
            self.spawned_vehicle.apply_control(self._control)
