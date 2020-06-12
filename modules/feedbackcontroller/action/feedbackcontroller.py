from PyQt5 import QtCore, QtWidgets, uic
import os, glob
import numpy as np
import math

import pandas as pd
import time

from modules.joanmodules import JOANModules

# #overriding the showpopup so that we can add new trajectories in the combobox on the go
# class ComboBox(QtWidgets.QComboBox):
#     popupAboutToBeShown = QtCore.pyqtSignal()

#     def showPopup(self):
#         self.popupAboutToBeShown.emit()
#         super(ComboBox, self).showPopup()

class FeedbackcontrollerAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.module_states = None
        self.module_state_handler = None
        try:
            state_package = self.get_module_state_package(module='modules.feedbackcontroller.widget.feedbackcontroller.FeedbackcontrollerWidget')
            self.module_states = state_package['module_states']
            self.module_state_handler = state_package['module_state_handler']
        except:
            pass

        # get state information from module Widget
        #self.module_states = 'module_states' in kwargs.keys() and kwargs['module_states'] or None
        #self.module_state_handler = 'module_state_handler' in kwargs.keys() and kwargs['module_state_handler'] or None


class Basecontroller():
    def __init__(self, FeedbackControllerWidget):
        self._parentWidget = FeedbackControllerWidget
        self._data= {}

    def process(self):
        return self._data

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
        if (DeltaPsi > math.pi):
            DeltaPsi = DeltaPsi - 2*math.pi
        if (DeltaPsi < -math.pi):
            DeltaPsi = DeltaPsi + 2*math.pi

        #print(DeltaDist, math.degrees(DeltaPsi))

        Error = np.array([DeltaDist, DeltaPsi])
        #Error[0] = DeltaPsi + DeltaDist

        
        #print(Error)

        return Error

    def closestNode(self, node, nodes):
        nodes = np.asarray(nodes)
        deltas = nodes - node
        dist_2 = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_2)

class Manualcontrol(Basecontroller):
    def __init__(self, FeedbackcontrollerWidget):
        Basecontroller.__init__(self, FeedbackcontrollerWidget)

        #Load the appropriate UI file
        self.manualTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Manual.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabWidget.addTab(self.manualTab,'Manual')
    
    def process(self):
        self._data = self._parentWidget.read_news(JOANModules.CARLA_INTERFACE)
        "Processes all information and returns parameters needed for steeringcommunication"
        return self._data

    

class FDCAcontrol(Basecontroller): #NOG NIET AF
    def __init__(self, FeedbackcontrollerWidget):
        # call super __init__
        Basecontroller.__init__(self, FeedbackcontrollerWidget)
        #Add the GUI Tab
        self._FDCATab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"FDCA.ui"))
        #self._FDCATab.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self._parentWidget.widget.tabWidget.addTab(self._FDCATab,'FDCA')


        # connect to widgets
        self._FDCATab.btnUpdate.clicked.connect(self.updateAvailableTrajectoryList)
        self._FDCATab.comboHCR.currentIndexChanged.connect(self.newHCRSelected)
        self._FDCATab.btnApply.clicked.connect(self.updateParameters)
        self._FDCATab.btnReset.clicked.connect(self.resetParameters)
        self._FDCATab.sliderKloha.valueChanged.connect(self.updateLoHA)

        #Initialize local Variables
        self._HCR = []
        self._HCRIndex = 0
        self._t_aheadFF = 0
        self._Ky = 0.1
        self._Kpsi = 0.4
        self._LoHS = 1
        self._SoHF = 1
        self._LoHA = 0

        #Set values on widget labels
        self._FDCATab.lblKyvalue.setText(str(self._Ky))
        self._FDCATab.lblKpsivalue.setText(str(self._Kpsi))
        self._FDCATab.lblKlohsvalue.setText(str(self._LoHS))
        self._FDCATab.lblKsohfvalue.setText(str(self._SoHF))
        self._FDCATab.lblKlohavalue.setText(str(self._LoHA))
        # path to HCR trajectory dir and add to list
        self._nameCurrentHCR = 'defaultHCRTrajectory.csv'
        self._pathHCRDirectory = os.path.join(os.path.dirname(os.path.realpath(__file__)),'HCRTrajectories')
        
        try:
            
            print(self._pathHCRDirectory)
            self.updateAvailableTrajectoryList()
            # load a default trajectory first
            idx = self._FDCATab.comboHCR.findText(self._nameCurrentHCR)
            if idx < 0:
                idx = 0 # in case the default trajectory file is not found, load the first one
            
            self._FDCATab.comboHCR.setCurrentIndex(idx) # this will also trigger the function newHCRSelected

        except Exception as e:
            print('Error loading list of available HCR trajectories: ', e)

    def updateLoHA(self):
        self._LoHA = self._FDCATab.sliderKloha.value()/100
        self._FDCATab.lblKlohavalue.setText(str(self._LoHA))

    def updateParameters(self):
        try:
            self._Ky = float(self._FDCATab.lineKy.text())
        except:
            pass
        try:
            self._Kpsi = float(self._FDCATab.lineKpsi.text())
        except:
            pass
        try:
            self._LoHS = float(self._FDCATab.lineKlohs.text())
        except:
            pass
        try:
            self._SoHF = float(self._FDCATab.lineKsohf.text())
        except:
            pass

        self._FDCATab.lblKyvalue.setText(str(self._Ky))
        self._FDCATab.lblKpsivalue.setText(str(self._Kpsi))
        self._FDCATab.lblKlohsvalue.setText(str(self._LoHS))
        self._FDCATab.lblKsohfvalue.setText(str(self._SoHF))

        self._FDCATab.lineKy.clear()
        self._FDCATab.lineKpsi.clear()
        self._FDCATab.lineKlohs.clear()
        self._FDCATab.lineKsohf.clear()

    def resetParameters(self):
        self._FDCATab.lineKy.clear()
        self._FDCATab.lineKpsi.clear()
        self._FDCATab.lineKlohs.clear()
        self._FDCATab.lineKsohf.clear()
        
        self._Ky = 0.1
        self._Kpsi = 0.4
        self._LoHS = 1
        self._SoHF = 1
        self._FDCATab.sliderKloha.setValue(0)

        self.updateParameters()


    def updateAvailableTrajectoryList(self):
        # get list of csv files in directory
        filenames = os.listdir(self._pathHCRDirectory)
        files = [ filename for filename in filenames if filename.endswith('csv') ]

        # os.chdir() # undesired change dir. 
        # files = glob.glob('*.{}'.format('csv'))


        # run through the combobox to check for files that are in the list, but not in the directory anymore
        listitems = [self._FDCATab.comboHCR.itemText(i) for i in range(self._FDCATab.comboHCR.count())]
        for l in listitems:
            if l not in files:
                idx = self._FDCATab.comboHCR.findText(l)
                if idx >= 0:
                    self._FDCATab.comboHCR.removeItem(idx)


        # self._FDCATab.comboHCR.clear() # we don't want this for reasons: (1) it resets the currentIndex(), which triggers a reload of a new trajectory, something we don't want to occur 'randomly'

        # add items that are in files but not yet in the combobox
        for fname in files:
            idx = self._FDCATab.comboHCR.findText(fname)
            if idx < 0:
                self._FDCATab.comboHCR.addItem(fname)
    

    def newHCRSelected(self):
        # new index selected

        # load based on filename, not index. Index can change if we remove items from the combobox list, which could yield undesired loading of HCR trajectories
        fname = self._FDCATab.comboHCR.itemText(self._FDCATab.comboHCR.currentIndex())

        if fname != self._nameCurrentHCR:
            # fname is different from _nameCurrentHCR, load it!
            print('Loading HCR trajectory: ' + fname)

            try:
                tmp = pd.read_csv(os.path.join(self._pathHCRDirectory, fname))
                self._HCR = tmp.values
            except Exception as e:
                print('Error loading HCR trajectory file (newHCRSelected): ', e)

            self._nameCurrentHCR = fname

        
    def process(self):
        try:
            self._data = self._parentWidget.read_news(JOANModules.CARLA_INTERFACE)
            print(self._data)
            egoCar = self._data['vehicles'][0].spawned_vehicle
            
            self._Error = self.Error_Calc(self._t_aheadFF, self._HCR, egoCar)
            print(self._Error)

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

            return self._data
        except Exception as e:
            print(e)
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



class PDcontrol(Basecontroller):
    def __init__(self, FeedbackcontrollerWidget):
        Basecontroller.__init__(self, FeedbackcontrollerWidget)

        #Load the appropriate UI file
        self._PDTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"PD.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabWidget.addTab(self._PDTab,'PD')

        #Attach apply button to variables
        self._PDTab.btnApply.clicked.connect(self.updateParameters)
        self._PDTab.btnReset.clicked.connect(self.resetParameters)


        #intialize class variables
        self._T1 = time.time()
        self._T2 = 0
        self._ErrorT2  = [0,0]
        self._t_ahead = 0.6
        self._Kp = 8
        self._Kd = 1
        self._Wlat = 1
        self._Whead = 2
        self._defaultHCR = 'defaultHCRTrajectory.csv'
        self._pathHCRDirectory = os.path.join(os.path.dirname(os.path.realpath(__file__)),'HCRTrajectories')
        tmp = pd.read_csv(os.path.join(self._pathHCRDirectory, self._defaultHCR))
        self._HCR = tmp.values

        # Show default values
        self._PDTab.lblPropgainvalue.setText(str(self._Kp))
        self._PDTab.lblDerivgainvalue.setText(str(self._Kd))
        self._PDTab.lblWeightlatvalue.setText(str(self._Wlat))
        self._PDTab.lblWeightheadingvalue.setText(str(self._Whead))
        self._PDTab.lblTaheadvalue.setText(str(self._t_ahead))
        
        
    def updateParameters(self):
        try:
            self._Kp = float(self._PDTab.linePropgain.text())
        except:
            pass
        try:
            self._Kd = float(self._PDTab.lineDerivgain.text())
        except:
            pass
        try:
            self._Wlat = float(self._PDTab.lineWeightlat.text())
        except:
            pass
        try:
            self._Whead = float(self._PDTab.lineWeightheading.text())
        except:
            pass
        try:
            self._t_ahead = float(self._PDTab.lineTahead.text())
        except:
            pass
       

        self._PDTab.lblPropgainvalue.setText(str(self._Kp))
        self._PDTab.lblDerivgainvalue.setText(str(self._Kd))
        self._PDTab.lblWeightlatvalue.setText(str(self._Wlat))
        self._PDTab.lblWeightheadingvalue.setText(str(self._Whead))
        self._PDTab.lblTaheadvalue.setText(str(self._t_ahead))

        self._PDTab.linePropgain.clear()
        self._PDTab.lineDerivgain.clear()
        self._PDTab.lineWeightlat.clear()
        self._PDTab.lineWeightheading.clear()
        self._PDTab.lineTahead.clear()

    def resetParameters(self):
        self._PDTab.linePropgain.clear()
        self._PDTab.lineDerivgain.clear()
        self._PDTab.lineWeightlat.clear()
        self._PDTab.lineWeightheading.clear()
        self._PDTab.lineTahead.clear()

        self._t_ahead = 0.6
        self._Kp = 8
        self._Kd = 1
        self._Wlat = 1
        self._Whead = 2

        self.updateParameters()
        

    def process(self):
        try:
            self._data= self._parentWidget.read_news(JOANModules.CARLA_INTERFACE)
            egoCar = self._data['egoCar']
            self._T1 = time.time()
            self._Error = self.Error_Calc(self._t_ahead, self._HCR, egoCar)
            DeltaT = self._T1 - self._T2
            DeltaError = self._Error - self._ErrorT2
            SWangle = self.PD(self._Error, DeltaError, DeltaT, self._Wlat, self._Whead, self._Kp, self._Kd)

            self._ErrorT2 = self._Error
            self._T2 = self._T1
            print(SWangle)
            return SWangle
        except Exception as e:
            print(e)
            return 0


    def PD(self, Error, DeltaError, DeltaT, WeightLat, WeightHeading, Kp, Kd):
        GainLat = WeightLat * (Kp * Error[0] + Kd*(DeltaError[0]/DeltaT))
        GainHeading = -WeightHeading * (Kp * Error[1] + Kd*(DeltaError[1]/DeltaT))

        SWangle = -(GainLat + GainHeading)/450
        
        return SWangle

    
    