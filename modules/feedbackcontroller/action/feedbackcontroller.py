from PyQt5 import QtCore
from PyQt5 import QtCore, QtWidgets, uic
import os

class Basecontroller():
    def __init__(self):
        self.data = {}

    def process(self):
        return self.data

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
        self.data = {}
        self.data['Damping']  = self.newtab.sliderDamping.value()
        self.data['Friction'] = self.newtab.sliderFriction.value()
        self.data['Spring']   = self.newtab.sliderSpring.value()

        
    def updatesliders(self):
        self.newtab.lblDamping.setText(str(self.newtab.sliderDamping.value())+ "mNm/rev/min")
        self.newtab.lblSpring.setText(str(self.newtab.sliderSpring.value())+ "mNm/deg")
        self.newtab.lblFriction.setText(str(self.newtab.sliderFriction.value())+ "mNm")
    
    def process(self):
        "Processes all information and returns parameters needed for steeringcommunication"
        self.data['Damping']  = self.newtab.sliderDamping.value()
        self.data['Friction'] = self.newtab.sliderFriction.value()
        self.data['Spring']   = self.newtab.sliderSpring.value()
        return self.data

    

class FDCAcontrol(Basecontroller): #NOG NIET AF
    def __init__(self, FeedbackcontrollerWidget):
        newtab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"FDCA.ui"))
        FeedbackcontrollerWidget.widget.tabWidget.addTab(newtab,'FDCA')
        self.data = {}

    def process(self):
        return self.data