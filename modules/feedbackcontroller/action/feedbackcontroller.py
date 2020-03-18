from PyQt5 import QtCore, QtWidgets, uic
import os, glob
from process import Control
import numpy as np

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

        self.FDCATab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"FDCA.ui"))
        self._parentWidget.widget.tabWidget.addTab(self.FDCATab,'FDCA')
        self.HCR = {}
        self.HCR[0] = "None"
        i = 1

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'HCRTrajectories/*.csv')
        #Laadt alle trajectories in uit de map HCR Trajectories
        for fname in glob.glob(path):
            self.FDCATab.comboHCR.addItem(os.path.basename(fname))
            self.HCR[i] = np.genfromtxt(fname, delimiter=',')
            i = i +1


        #connect change of HCR
        self.FDCATab.comboHCR.currentIndexChanged.connect(self.selectHCR)


    def process(self):
        self.data = self._parentWidget.readNews('modules.carlainterface.widget.carlainterface.CarlainterfaceWidget')
        print(self.data)
        # self.Error = self.Error_Calc_wrt_HCR(self.T_aheadFF)

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

    def selectHCR(self):
        self.HCRIndex = self.FDCATab.comboHCR.currentIndex()
        print(self.HCR[self.HCRIndex])