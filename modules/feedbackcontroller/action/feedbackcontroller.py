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
        self.data = {}

    
    def process(self):
        "Processes all information and returns parameters needed for steeringcommunication"
        return self.data

    

class FDCAcontrol(Basecontroller): #NOG NIET AF
    def __init__(self, FeedbackcontrollerWidget):
        newtab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"FDCA.ui"))
        FeedbackcontrollerWidget.widget.tabWidget.addTab(newtab,'FDCA')
        self.data = {}

    def process(self):
        self.data['FDCA Data Dingetje'] = 'hey hallo ik ben awesome'
        return self.data