import time
import random
import os
import sys
import glob

from PyQt5 import QtCore, QtWidgets, uic
from process import Control

try:
    sys.path.append(glob.glob('../../carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    import carla  # Hier heb ik dus de PC voor nodig error is onzin!

except IndexError:
    pass

class CarlainterfaceAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        # get state information from module Widget
        self.module_states = 'module_states' in kwargs.keys() and kwargs['module_states'] or None
        self.module_state_handler = 'module_state_handler' in kwargs.keys() and kwargs['module_state_handler'] or None


class Carlacommunication():
    """
    Class variables are used to have access to blueprints initialized already
    """

    def __init__(self, CarlainterfaceWidget):  # Initialize the variables needed to connect, and data structure to put collected data in
        print('Carla Communication constructed')
        self._parentWidget = CarlainterfaceWidget.widget
        Carlacommunication.carlaData = {}
        self.host = 'localhost'
        self.port = 2000
        Carlacommunication.tags = []

    def connect(self):
        try:
            print(' connecting')
            client = carla.Client(self.host, self.port)  # connecting to server
            client.set_timeout(2.0)
            time.sleep(2)
            Carlacommunication.world = client.get_world()  # get world object (contains everything)
            Carlacommunication.BlueprintLibrary = Carlacommunication.world.get_blueprint_library()
            vehicle_bp_library = Carlacommunication.BlueprintLibrary.filter('vehicle.*')
            for items in vehicle_bp_library:
                Carlacommunication.tags.append(items.id[8:])
            world_map = Carlacommunication.world.get_map()
            Carlacommunication.spawn_points = world_map.get_spawn_points()
            Carlacommunication.nr_spawn_points = len(self.spawn_points)
            print('JOAN connected to CARLA Server!')

            return True
        except RuntimeError as inst:
            print('Could not connect error given:', inst)
            return False


class Carlavehicle(Carlacommunication):
    def __init__(self, CarlainterfaceWidget, carnr):
        self._parentWidget = CarlainterfaceWidget
        self._vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "vehicletab.ui"))
        self._parentWidget.widget.layOut.addWidget(self._vehicle_tab)
        self._vehicle_tab.group_car.setTitle('Car ' + str(carnr+1))
        self._spawned = False
        self._hardware_data = {}

        self._vehicle_tab.spin_spawn_points.setRange(0, Carlacommunication.nr_spawn_points)
        self._vehicle_tab.spin_spawn_points.lineEdit().setReadOnly(True)
        self._vehicle_tab.btn_destroy.setEnabled(False)
        self._vehicle_tab.combo_input.currentTextChanged.connect(self.update_input)

        self._vehicle_tab.btn_spawn.clicked.connect(self.spawn_car)
        self._vehicle_tab.btn_destroy.clicked.connect(self.destroy_car)
        for item in Carlacommunication.tags:
            self._vehicle_tab.comboCartype.addItem(item)

        self._selected_input = str('None')

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
        self._hardware_data = self._parentWidget.read_news('modules.hardwarecommunication.widget.hardwarecommunication.HardwarecommunicationWidget')
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
        self._BP = random.choice(Carlacommunication.BlueprintLibrary.filter("vehicle." + str(self._vehicle_tab.comboCartype.currentText())))
        self._control = carla.VehicleControl()
        try:
            spawnpointnr = self._vehicle_tab.spin_spawn_points.value()-1
            self.spawned_vehicle = Carlacommunication.world.spawn_actor(self._BP, Carlacommunication.spawn_points[spawnpointnr])
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
