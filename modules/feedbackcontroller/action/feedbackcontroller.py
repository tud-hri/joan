from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5 import QtCore, QtWidgets, uic
import os

class Basecontroller():
    def __init__(self):
        pass

    def process(self):
        pass
    
    def printshit(self):
        print('basecontrollershit')

class Manualcontrol(Basecontroller):
    def __init__(self, FeedbackcontrollerWidget):
        #Load the appropriate UI file
        self.newtab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"Manual.ui"))
        #Add ui file to a new tab
        FeedbackcontrollerWidget.widget.tabWidget.addTab(self.newtab,'Manual')

        #attach sliders and inputs to functions within this class
        self.newtab.sliderDamping.valueChanged.connect(self.updatesliders)
        self.newtab.sliderFriction.valueChanged.connect(self.updatesliders)
        self.newtab.sliderSpring.valueChanged.connect(self.updatesliders)

        
    def updatesliders(self):
        self.newtab.lblDamping.setText(str(self.newtab.sliderDamping.value())+ "mNm/rev/min")
        self.newtab.lblSpring.setText(str(self.newtab.sliderSpring.value())+ "mNm/deg")
        self.newtab.lblFriction.setText(str(self.newtab.sliderFriction.value())+ "mNm")

    def printshit(self):
        print('Manual Control Shit')


    
    
    def process(self):
        "Processes all information and returns calculated torque"
        pass

    

class FDCAcontrol(Basecontroller): #NOG NIET AF
    def __init__(self, FeedbackcontrollerWidget):
        newtab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"FDCA.ui"))
        FeedbackcontrollerWidget.widget.tabWidget.addTab(newtab,'FDCA')
        pass

    def printshit(self):
        print('FDCA Control Shit')