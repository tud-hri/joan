from process import Control
import numpy as np

class TrajectoryrecorderAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        # get state information from module Widget
        self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or None
        self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None
        self.data = [0, 0, 0, 0, 0, 0]
        self.TrajData = ([1,2,3,4,5,6],[2,3,4,5,6,7])
        self.Traveled = 0
        self.OverallDist = 0

    
    def process(self, data):
        PosX = data['egoCar'].get_transform().location.x
        PosY = data['egoCar'].get_transform().location.y
        SteeringAngle = data['egoCar'].control.steer
        Throttle = data['egoCar'].control.throttle
        Brake = data['egoCar'].control.brake
        Psi = data['egoCar'].get_transform().rotation.yaw

        self.data = np.append(self.data, [PosX, PosY, SteeringAngle, Throttle, Brake, Psi], axis = 0)

        self.maketrajectoryarray(0.1)
        print(self.TrajData)

    def maketrajectoryarray(self, waypointDistance):
        tempdiff = self.data[-1] - self.data[-2]
        posdiff = tempdiff[0:2]
        smallDist = np.linalg.norm(posdiff)
        self.OverallDist = self.OverallDist + smallDist
        self.Traveled = self.Traveled + smallDist
        if(self.OverallDist >= waypointDistance):
            self.TrajData = np.append(self.TrajData,[self.data[-1]], axis = 0)
            self.OverallDist = self.OverallDist - waypointDistance

    def generate(self):
        return self.TrajData
        print(self.TrajData)


        