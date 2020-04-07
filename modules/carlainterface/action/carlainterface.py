import time
import random
import os
import sys
import glob

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
    def __init__(self, CarlainterfaceWidget):  # Initialize the variables needed to connect, and data structure to put collected data in
        print('Carla Communication constructed')
        self._parentWidget = CarlainterfaceWidget.widget
        self.carlaData = {}
        self.carlaData['egoCar'] = None
        self.host = 'localhost'
        self.port = 2000

    def start(self):
        print(' connecting')
        self.client = carla.Client(self.host, self.port)  # connecting to server
        # self._parentWidget.lblModuleState.setText('Connecting')
        self.client.set_timeout(2.0)
        time.sleep(2)
        self.world = self.client.get_world()  # get world object (contains everything)
        # JUST TO SHOW THAT THE CLIENT CONNECTS (weather has no other uses)
        # self.weather = self.world.get_weather()
        # self.weather.cloudyness = 30
        # self.weather.sun_azimuth_angle = 180
        # self.weather.sun_altitude_angle = 90
        # self.weather.precipitation = 0
        # self.weather.precipitation_deposits = 0
        # self.world.set_weather(self.weather)

        self.BlueprintLibrary = self.world.get_blueprint_library()
        self.vehicleBPlibrary = self.BlueprintLibrary.filter('vehicle.*')
        self.walkerBPlibrary = self.BlueprintLibrary.filter('walker.pedestrian.*')
        self.worldMap = self.world.get_map()
        self.spawnPoints = self.worldMap.get_spawn_points()
        self.nrSpawnPoints = len(self.spawnPoints)
        self.control = carla.VehicleControl()

        self.egoCarBP = random.choice(self.BlueprintLibrary.filter("vehicle.HapticsLab.*"))
        self.egoCar = self.world.spawn_actor(self.egoCarBP, self.spawnPoints[0])
        #self._parentWidget.lblModuleState.setText('Car Spawned')

        return True
        # except Exception as inst:
        #     self.egoCar = None
        #     print('Could not connect error given:', inst)
        #     return False

    def stop(self):
        print('stopped')

    def getData(self):
        self.carlaData['egoCar'] = self.egoCar
        return self.carlaData

    def handleFeedbackcontrollerdata(self, data):
        try:
            SWangle = data['SteeringWheelAngle']
            Throttle = data['Throttle']
            self.control.steer = SWangle
            self.control.throttle = Throttle
        except:
            pass

        self.egoCar.apply_control(self.control)

    def setInputs(self, inputs):
        steering = inputs['SteeringInput'] / 450
        throttle = inputs['ThrottleInput'] / 100
        brake = inputs['BrakeInput'] / 100

        self.control.steer = steering
        self.control.throttle = throttle
        self.control.brake = brake

        self.egoCar.apply_control(self.control)
