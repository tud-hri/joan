from process import Control
from PyQt5 import uic
import os

class HardwarecommunicationAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        # get state information from module Widget
        self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or None
        self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None


class BaseInput():
    def __init__(self, HardwarecommunicationWidget):
        self._parentWidget = HardwarecommunicationWidget
        self._data= {}
        self.usingText = 'None'
        self.setUsingtext()

    def process(self):
        return self._data

    def setUsingtext(self):
        self._parentWidget.widget.lblSource.setText(self.usingText)


class Keyboard(BaseInput):
    def __init__(self,HardwarecommunicationWidget):
        BaseInput.__init__(self, HardwarecommunicationWidget)
        self.usingText = 'Keyboard'
        #Load the appropriate UI file
        self._keyboardTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"keyboard.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabInputs.addTab(self._keyboardTab,'Keyboard')

        self._keyboardTab.btnUse.clicked.connect(self.setUsingtext)

        

class Mouse(BaseInput):
    def __init__(self,HardwarecommunicationWidget):
        BaseInput.__init__(self, HardwarecommunicationWidget)
        self.usingText = 'Mouse'
        #Load the appropriate UI file
        self._mouseTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"mouse.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabInputs.addTab(self._mouseTab,'Mouse')

        self._mouseTab.btnUse.clicked.connect(self.setUsingtext)