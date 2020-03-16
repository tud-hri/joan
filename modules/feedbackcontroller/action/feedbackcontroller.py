from PyQt5 import QtCore
from PyQt5 import QtCore, QtWidgets, uic
import os
class Manualcontrol():
    def __init__(self, FeedbackcontrollerWidget):
        newtab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"basic.ui"))
        FeedbackcontrollerWidget.widget.tabWidget.addTab(newtab,'Manual')
        pass

    def process(self):
        "Processes all information and returns calculated torque"
        pass

    

class FDCAcontrol():
    def __init__(self, FeedbackcontrollerWidget):
        newtab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"basic.ui"))
        FeedbackcontrollerWidget.widget.tabWidget.addTab(newtab,'FDCA')
        pass