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
        self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or None
        self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None


class Carlacommunication():
    """
    Class variables are used to have access to blueprints initialized already
    """
    def __init__(self, CarlainterfaceWidget):  # Initialize the variables needed to connect, and data structure to put collected data in
        print('Carla Communication constructed')
        self._parentWidget = CarlainterfaceWidget.widget
        self.carlaData = {}
        self.carlaData['egoCar'] = None
        self.host = 'localhost'
        self.port = 2000

    def connect(self):
        try:
            print(' connecting')
            client = carla.Client(self.host, self.port)  # connecting to server
            # self._parentWidget.lblModuleState.setText('Connecting')
            client.set_timeout(2.0)
            time.sleep(2)
            world = client.get_world()  # get world object (contains everything)
            Carlacommunication.BlueprintLibrary = world.get_blueprint_library()
            worldMap = world.get_map()
            Carlacommunication.spawnPoints = worldMap.get_spawn_points()
            Carlacommunication.nrSpawnPoints = len(self.spawnPoints)
            print('JOAN connected to CARLA Server!')

            return True
        except Exception as inst:
            self.egoCar = None
            print('Could not connect error given:', inst)
            return False

    def getData(self):
        self.carlaData['egoCar'] = self.egoCar
        return self.carlaData

    def setInputs(self, inputs):
        steering = inputs['SteeringInput'] / 450
        throttle = inputs['ThrottleInput'] / 100
        brake = inputs['BrakeInput'] / 100

        self.control.steer = steering
        self.control.throttle = throttle
        self.control.brake = brake

        self.egoCar.apply_control(self.control)

class Carlavehicle(Carlacommunication):
    def __init__(self, CarlainterfaceWidget, carnr):
        self._parentWidget = CarlainterfaceWidget.widget
        self._vehicleTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"vehicletab.ui"))
        self._parentWidget.layOut.addWidget(self._vehicleTab)
        self._vehicleTab.groupCar.setTitle('Car ' + str(carnr+1))

        self._vehicleTab.spinSpawnpoints.setRange(0, Carlacommunication.nrSpawnPoints)
        self._vehicleTab.spinSpawnpoints.lineEdit().setReadOnly(True)

        # Initialize Vehicle
        self._BP = random.choice(Carlacommunication.BlueprintLibrary.filter("vehicle.HapticsLab.*"))
        
    def destroyTab(self):
        self._parentWidget.layOut.removeWidget(self._vehicleTab)
        self._vehicleTab.setParent(None)

    def spawn(self):
        spawnpointnr = self._vehicleTab.spinSpawnpoints.value()
        self.spawnedVehicle = 
        pass