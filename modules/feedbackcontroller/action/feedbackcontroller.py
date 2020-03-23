from PyQt5 import QtCore, QtWidgets, uic
import os, glob
from process import Control
import numpy as np
import math

#overriding the showpopup so that we can add new trajectories in the combobox on the go
class ComboBox(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        print('showing')
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()

class FeedbackcontrollerAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        # get state information from module Widget
        self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or None
        self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None


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
        #self.FDCATab.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self._parentWidget.widget.tabWidget.addTab(self.FDCATab,'FDCA')

        #Add the new popup signal so and adjust layout accordingly
        self.FDCATab.comboHCRnew = ComboBox(self.FDCATab.comboHCR)
        self.FDCATab.comboHCRnew.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.ExtraLayout = QtWidgets.QGridLayout()
        self.ExtraLayout.setContentsMargins(0,0,0,0)
        self.ExtraLayout.addWidget(self.FDCATab.comboHCRnew)
        self.FDCATab.comboHCR.setLayout(self.ExtraLayout)
        
        
        
        #Initialize local Variables
        self.HCR = {}
        self.HCRIndex = 0
        self.t_aheadFF = 0

        #Load all available Human Compatible References
        i = 0
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'HCRTrajectories/*.csv')

        


        for fname in glob.glob(path):
            self.FDCATab.comboHCRnew.addItem(os.path.basename(fname))
            self.HCR[i] = np.genfromtxt(fname, delimiter=',')
            i = i +1


        #connect change of HCR
        #self.FDCATab.comboHCRJoe.setFocus()
        self.FDCATab.comboHCRnew.popupAboutToBeShown.connect(self.addallavailabletrajectories)
        self.FDCATab.comboHCRnew.currentIndexChanged.connect(self.selectHCR)


    def addallavailabletrajectories(self):
        self.FDCATab.comboHCRnew.clear()
        i = 0
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'HCRTrajectories/*.csv')
        for fname in glob.glob(path):
            self.FDCATab.comboHCRnew.addItem(os.path.basename(fname))
            self.HCR[i] = np.genfromtxt(fname, delimiter=',')
            i = i +1

    def selectHCR(self):
        self.HCRIndex = self.FDCATab.comboHCR.currentIndex()
        print(len(self.HCR))
        

    def process(self):
        self.data = self._parentWidget.readNews('modules.siminterface.widget.siminterface.SiminterfaceWidget')
        egoCar = self.data['egoCar']
        self.Error = self.Error_Calc(self.t_aheadFF, self.HCR[self.HCRIndex], egoCar)
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
        CarLocation = car.get_location()
        CarVelocity = car.get_velocity()
        CarTransform = car.get_transform()

        egoLocation = np.array([CarLocation.x, CarLocation.y])

        egoVel = np.array([CarVelocity.x , CarVelocity.y])
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
        
        PsiCar = CarTransform.rotation.yaw
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

        
        #print(Error)

        return Error

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


