from PyQt5 import QtCore, QtWidgets
import os, sys, glob
from process import Control

# try:
#     sys.path.append(glob.glob('../../carla/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
#         sys.version_info.major,
#         sys.version_info.minor,
#         'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
# except IndexError:
#     pass

#import carla Hier heb ik dus de PC voor nodig 

# This class will always be constructed whenever you decide to use (show) the widget
class Simcommunication():
    def __init__(self):  # Initialize the variables needed to connect, and data structure to put collected data in
        print('Carla Communication constructed')
        self.carlaData = {}
        self.carlaData['egoLocation']     = [0, 0, 0]
        self.carlaData['egoVelocity']     = [0, 0, 0]
        self.carlaData['egoTransform'] = [0, 0, 0, 0 ,0,0]

        self.host = 'localhost'
        self.port = 2000
        

    def start(self):
        try:
            print(' connecting')
            #self.client = carla.Client(self.host,self.port) #connecting to server
        except:
            print('could not connect')
        pass

    def stop(self):
        print('stopped')

    def getData(self):
        self.carlaData['egoLocation'][0]  = self.carlaData['egoLocation'][0] - 0.01
        self.carlaData['egoLocation'][1]  = self.carlaData['egoLocation'][1] - 0.01
        #self.carlaData['egoCar']     = self.egoCar
        # self.carlaData['egoCarVelocity']     = self.egoCar.get_transform()
        # self.carlaData['egoCarAcceleration'] = self.egoCar.get_acceleration()


        return self.carlaData
