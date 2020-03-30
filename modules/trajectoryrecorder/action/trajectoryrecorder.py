from process import Control
import numpy as np

class TrajectoryrecorderAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        # get state information from module Widget
        self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or None
        self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None
        self._data = [0, 0, 0, 0, 0, 0]
        self._TrajData = ([1,2,3,4,5,6],[2,3,4,5,6,7])
        self._Traveled = 0
        self._OverallDist = 0

    
    def process(self, _data):
        PosX = _data['egoCar'].get_transform().location.x
        PosY = _data['egoCar'].get_transform().location.y
        SteeringAngle = _data['egoCar'].control.steer
        Throttle = _data['egoCar'].control.throttle
        Brake = _data['egoCar'].control.brake
        Psi = _data['egoCar'].get_transform().rotation.yaw

        self._data = np.append(self._data, [PosX, PosY, SteeringAngle, Throttle, Brake, Psi], axis = 0)

        self.maketrajectoryarray(0.1)
        print(self._TrajData)

    def maketrajectoryarray(self, waypointDistance):
        tempdiff = self._data[-1] - self._data[-2]
        posdiff = tempdiff[0:2]
        smallDist = np.linalg.norm(posdiff)
        self._OverallDist = self._OverallDist + smallDist
        self._Traveled = self._Traveled + smallDist
        if(self._OverallDist >= waypointDistance):
            self._TrajData = np.append(self._TrajData,[self._data[-1]], axis = 0)
            self._OverallDist = self._OverallDist - waypointDistance

    def generate(self):
        return self._TrajData



        