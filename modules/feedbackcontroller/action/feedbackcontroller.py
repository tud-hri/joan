from PyQt5 import QtCore, QtWidgets, uic
import os, glob
from process import Control
import numpy as np
import math

class Basecontroller():
    def __init__(self, FeedbackControllerWidget):
        self._parentWidget = FeedbackControllerWidget
        self.data = {}

    def process(self):
        return self.data

class Manualcontrol(Basecontroller):
    def __init__(self, FeedbackcontrollerWidget):
        Basecontroller.__init__(self, FeedbackcontrollerWidget)

        #Load the appropriate UI file
        self.manualTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Manual.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabWidget.addTab(self.manualTab,'Manual')
    
    def process(self):
        "Processes all information and returns parameters needed for steeringcommunication"
        return self.data

    

class FDCAcontrol(Basecontroller): #NOG NIET AF
    def __init__(self, FeedbackcontrollerWidget):
        # call super __init__
        Basecontroller.__init__(self, FeedbackcontrollerWidget)
        #Add the GUI Tab
        self.FDCATab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"FDCA.ui"))
        self._parentWidget.widget.tabWidget.addTab(self.FDCATab,'FDCA')
        
        #Initialize local Variables
        self.HCR = {}
        self.HCRIndex = 0
        self.t_aheadFF = 0

        #Load all available Human Compatible References
        i = 0
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'HCRTrajectories/*.csv')
        for fname in glob.glob(path):
            self.FDCATab.comboHCR.addItem(os.path.basename(fname))
            self.HCR[i] = np.genfromtxt(fname, delimiter=',')
            i = i +1


        #connect change of HCR
        self.FDCATab.comboHCR.currentIndexChanged.connect(self.selectHCR)


    def process(self):
        self.data = self._parentWidget.readNews('modules.carlainterface.widget.carlainterface.CarlainterfaceWidget')

        self.Error = self.Error_Calc(self.t_aheadFF, self.HCR[self.HCRIndex], self.data)
        print(self.Error)

        # ## GAINS  (FDCA as in SIMULINK)
        # SWAngle_FB = self.SoHFFunc(self.K_y,self.K_psi,self.SoHF,self.Error[0],self.Error[1])
         
        # SWAngle_FFdes = self.FeedForwardController(0)
          
        # SWAngle_FF = self.LoHSFunc(self.LoHS,SWAngle_FFdes)

        # SWAngleFB_FFDes = SWAngle_FB + SWAngle_FFdes #in radians

        # SWAngle_Current = math.radians(self.Angle)

        # delta_SW = SWAngleFB_FFDes - SWAngle_Current

        # SWAngle_FF_FB = SWAngle_FF + SWAngle_FB

        # Torque_LoHA = self.LoHAFunc(self.LoHA, delta_SW) #Torque resulting from feedback
              
        # K_stiffnessDeg = 40 # 40mNm/deg [DEGREES! CONVERT TO RADIANS!!]

        # K_stiffnessRad = K_stiffnessDeg  * (math.pi/180)

        # Torque_FF_FB = self.InverseSteeringDyn(SWAngle_FF_FB,K_stiffnessRad)

        # Torque_FDCA = Torque_LoHA + Torque_FF_FB

        # intTorque = int(round(Torque_FDCA*1000))

        # TorqueBytes = int.to_bytes(intTorque,2, byteorder = 'little',signed= True)

        return self.data


    def Error_Calc(self, t_ahead, trajectory, car):
        # The error contains both the lateral error and the heading error(t_ahead is how many seconds we look forward)
        CarLocation = car['egoLocation']
        CarVelocity = car['egoVelocity']
        CarTransform = car['egoTransform']


        egoLocation = np.array([CarLocation[0], CarLocation[1]])

        egoVel = np.array([CarVelocity[0] , CarVelocity[1]])
        ExtraDistance = egoVel * t_ahead

        FutureLocation = egoLocation + ExtraDistance

        
        
        # Find waypoint index of the point that the car would be in the future (compared to own driven trajectory)
        NWPFutureIndex = self.closestNode(FutureLocation, trajectory[:, 1:3])
        if(NWPFutureIndex >= len(trajectory)-3):
            NWPFutureIndexPlus1 = 0
        else:
            NWPFutureIndexPlus1 = NWPFutureIndex + 3
            
        ## Calculate Lateral Error (DeltaDist)
        FutureLocationOnTrajectory = trajectory[NWPFutureIndex, 1:3]
        FutureLocationOnTrajectoryNext = trajectory[NWPFutureIndexPlus1, 1:3]

       

        FutLocVec = FutureLocation - FutureLocationOnTrajectory
        FutDirVec = FutureLocationOnTrajectoryNext - FutureLocationOnTrajectory

        

        Sign = np.math.atan2(np.linalg.det([FutDirVec,FutLocVec]),np.dot(FutDirVec,FutLocVec))

        DeltaDist = np.sqrt(FutLocVec.dot(FutLocVec))
        
        if (Sign < 0):
            DeltaDist = -DeltaDist

        #print("FutureLocation On Trajectory = " ,  FutureLocationOnTrajectory, "Future Location Next= " ,FutureLocationOnTrajectoryNext, "FutDirVec = ", FutDirVec, "FutLocVec =", FutLocVec , "Angle Between =" , Sign, "Lat Error=", DeltaDist)        


        #Calculate Heading Error (DeltaPsi)

        #ForwardVector = CarTransform.rotation.get_forward_vector()
        
        PsiCar = CarTransform[2]
        PsiTraj = trajectory[NWPFutureIndex, 6]
        

     
        DeltaPsi = -((math.radians(PsiCar) - math.radians(PsiTraj)))

        #Make sure you dont get jumps (basically unwrap the angle with a threshold of pi radians (180 degrees))
        if(DeltaPsi > math.pi):
            DeltaPsi = DeltaPsi - 2*math.pi
        if(DeltaPsi < -math.pi):
            DeltaPsi = DeltaPsi + 2*math.pi

        #print(DeltaDist, math.degrees(DeltaPsi))

        Error = np.array([DeltaDist, DeltaPsi])
        #Error[0] = DeltaPsi + DeltaDist

        


        return Error

        #### FDCA WITH SAME NOMENCLATURE AS SIMULINK

    def SoHFFunc(self, Ky, Kpsi,SoHF, DeltaY, DeltaPsi):
        Temp = SoHF* (Ky * DeltaY + Kpsi * DeltaPsi)

        return Temp

    def FeedForwardController(self, t_ahead):
        if(hasattr(self,'egoCar')):
            self.egoCarLocation = self.egoCar.get_location()
            self.egoCarVelocity = self.egoCar.get_velocity()
            self.egoCarTransform = self.egoCar.get_transform()

            egoLocation = np.array([self.egoCarLocation.x, self.egoCarLocation.y])
            egoVel = np.array([self.egoCarVelocity.x , self.egoCarVelocity.y])
            ExtraDistance = egoVel * t_ahead

            FutureLocation = egoLocation + ExtraDistance

            FeedForwardIndex = self.closestNode(FutureLocation, self.Traj1XY)
            if(FeedForwardIndex >= len(self.Traj1XY)-20):
                FeedForwardIndexPlus1 = 0
            else:
                FeedForwardIndexPlus1 = FeedForwardIndex + 20


            SWangle_FFdes = math.radians(self.Trajectory1[FeedForwardIndexPlus1, 3]*450)

            return SWangle_FFdes

        else:
            return 0

    def LoHSFunc(self,LoHS,SWangle_FFDES):
        SWangle_FF = SWangle_FFDES * LoHS

        return SWangle_FF

    def LoHAFunc(self, LoHA, delta_SW):
        Torque_LoHA = LoHA * delta_SW

        
        return Torque_LoHA

    def InverseSteeringDyn(self, SWangle,K_Stiffness):
        Torque = SWangle * 1/(1.0/K_Stiffness)

        return Torque

        # Method to find the closest waypoint to predefined list
    def closestNode(self, node, nodes):
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_2 = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_2)


    def selectHCR(self):
        self.HCRIndex = self.FDCATab.comboHCR.currentIndex()
        print(self.HCR[self.HCRIndex])