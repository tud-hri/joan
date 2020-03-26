from process import Control
from PyQt5 import uic, QtCore, QtGui
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
        self._data = {}
        self._data['SteeringAngleInput'] = 0
        self._data['ThrottleInput']      = 0
        self._data['GearShiftInput']     = 0
        self._data['BrakeInput']         = 0
        self._data['Reverse']            = False

        self.currentInput = 'None'
        self.setUsingtext()


    def process(self):
        pass

    def changeInputSource(self):
        self._parentWidget._input = self._parentWidget.Inputs[self.currentInput]
        self.setUsingtext()

    def setUsingtext(self):
        self._parentWidget.widget.lblSource.setText(self.currentInput)

    def displayInputs(self):
        self._parentWidget.widget.sliderSteering.setValue(self._data['SteeringAngleInput'])



class Keyboard(BaseInput):
    def __init__(self,HardwarecommunicationWidget):
        BaseInput.__init__(self, HardwarecommunicationWidget)
        self.currentInput = 'Keyboard'
        #Load the appropriate UI file
        self._keyboardTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"keyboard.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabInputs.addTab(self._keyboardTab,'Keyboard')

        self._keyboardTab.btnUse.clicked.connect(self.setCurrentInput)

        self._parentWidget.mainwidget.keyPressEvent = self.keyPressEvent

    
        #self._keyboardTab.keyPressEvent = self.keyPressEvent
        ## initialize pygame

        # FIRE = 123
        # self.pevent = pygame.event.Event(FIRE, message="Bad cat!")

    def keyPressEvent(self,event):
        if(self._parentWidget.widget.lblSource.text() == 'Keyboard'):
            print(event.key())

    def setCurrentInput(self):
        self.currentInput = 'Keyboard'
        self.changeInputSource()

    def displayInputs(self):
        self._data['SteeringAngleInput'] = 180
        self._parentWidget.widget.sliderSteering.setValue(self._data['SteeringAngleInput'])
        #print('keyboard')

    def process(self):
        #print(self.currentInput)
        pass


        

    

        

class Mouse(BaseInput):
    def __init__(self,HardwarecommunicationWidget):
        BaseInput.__init__(self, HardwarecommunicationWidget)
        self.currentInput = 'Mouse'
        #Load the appropriate UI file
        self._mouseTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"mouse.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabInputs.addTab(self._mouseTab,'Mouse')

        self._mouseTab.btnUse.clicked.connect(self.setCurrentInput)

    def displayInputs(self):
        self._data['SteeringAngleInput'] = -180
        self._parentWidget.widget.sliderSteering.setValue(self._data['SteeringAngleInput'])
        print(self.currentInput)

    def setCurrentInput(self):
        self.currentInput = 'Mouse'
        self.changeInputSource()
        
    def process(self):
        #print(self.currentInput)
        pass