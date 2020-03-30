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
        self._data['SteeringInput'] = 0
        self._data['ThrottleInput']      = 0
        self._data['GearShiftInput']     = 0
        self._data['BrakeInput']         = 0
        self._data['Reverse']            = False

        self.currentInput = 'None'
        self.setUsingtext()

        self._parentWidget.widget.sliderThrottle.setEnabled(False)
        self._parentWidget.widget.sliderSteering.setEnabled(False)
        self._parentWidget.widget.sliderBrake.setEnabled(False)
        self.steerRange = 180 #range until


    def process(self):
        return self._data
        

    def changeInputSource(self):
        self._parentWidget._input = self._parentWidget.Inputs[self.currentInput]
        self.setUsingtext()

    def setUsingtext(self):
        self._parentWidget.widget.lblSource.setText(self.currentInput)

    def displayInputs(self):
        pass



class Keyboard(BaseInput):
    def __init__(self,HardwarecommunicationWidget):
        BaseInput.__init__(self, HardwarecommunicationWidget)
        self.currentInput = 'Keyboard'
        #Load the appropriate UI file
        self._keyboardTab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"keyboard.ui"))
        #Add ui file to a new tab
        self._parentWidget.widget.tabInputs.addTab(self._keyboardTab,'Keyboard')

        self._keyboardTab.btnUse.clicked.connect(self.setCurrentInput)

        self._parentWidget.window.keyPressEvent = self.keyPressEvent
        self._parentWidget.window.keyReleaseEvent = self.keyReleaseEvent
        self.steerLeft = False
        self.steerRight = False
        self.throttle = False
        self.brake = False
        self.reverse = False
        


    def keyPressEvent(self,event):
        if(self._parentWidget.widget.lblSource.text() == 'Keyboard'):
            key = event.key()
            if key == QtCore.Qt.Key_Up: 
                self.throttle = True
            elif key == QtCore.Qt.Key_Space:
                self.brake = True
            elif key == QtCore.Qt.Key_A:
                self.steerLeft = True
                self.steerRight = False
            elif key == QtCore.Qt.Key_D:
                self.steerRight = True
                self.steerLeft = False

    def keyReleaseEvent(self,event):
        if(self._parentWidget.widget.lblSource.text() == 'Keyboard'):
            key = event.key()
            if key == QtCore.Qt.Key_Up: 
                self.throttle = False
            elif key == QtCore.Qt.Key_Space:
                self.brake = False
            elif key == QtCore.Qt.Key_A:
                self.steerLeft = False
                self.steerRight = False
            elif key == QtCore.Qt.Key_D:
                self.steerRight = False
                self.steerLeft = False
            elif key == QtCore.Qt.Key_R:
                if(self.reverse == False):
                    self.reverse = True
                elif(self.reverse == True):
                    self.reverse = False


    def setCurrentInput(self):
        self.currentInput = 'Keyboard'
        self._parentWidget.widget.sliderThrottle.setEnabled(False)
        self._parentWidget.widget.sliderSteering.setEnabled(False)
        self._parentWidget.widget.sliderBrake.setEnabled(False)
        self.changeInputSource()

    def displayInputs(self):
        #update sliders and reverse label
        self._parentWidget.widget.sliderThrottle.setValue(self._data['ThrottleInput'])
        self._parentWidget.widget.sliderSteering.setValue(self._data['SteeringInput'])
        self._parentWidget.widget.sliderBrake.setValue(self._data['BrakeInput'])
        self._parentWidget.widget.lblReverse.setText(str(self.reverse))

        #set values next to sliders:
        self._parentWidget.widget.lblThrottle.setText(str(self._data['ThrottleInput']))
        self._parentWidget.widget.lblSteering.setText(str(self._data['SteeringInput']))
        self._parentWidget.widget.lblBrake.setText(str(self._data['BrakeInput']))

    def process(self):
        #Throttle:
        if(self.throttle == True and self._data['ThrottleInput'] < 100 ):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] +2.5
        elif(self._data['ThrottleInput'] > 0 and self.throttle == False):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] - 2.5

        #Brake:
        if(self.brake == True and self._data['BrakeInput'] < 100 ):
            self._data['BrakeInput'] = self._data['BrakeInput'] +5
        elif(self._data['BrakeInput'] > 0 and self.brake == False):
            self._data['BrakeInput'] = self._data['BrakeInput'] -5

        #Steering:
        if(self.steerLeft == True and self._data['SteeringInput'] < self.steerRange and self._data['SteeringInput'] > -self.steerRange):
            self._data['SteeringInput'] = self._data['SteeringInput'] - 2
        elif(self.steerRight == True and self._data['SteeringInput'] > -self.steerRange and self._data['SteeringInput'] < self.steerRange):
            self._data['SteeringInput'] = self._data['SteeringInput'] + 2
        elif(self._data['SteeringInput'] > 0):
            self._data['SteeringInput'] = self._data['SteeringInput'] -1
        elif(self._data['SteeringInput'] < 0):
            self._data['SteeringInput'] = self._data['SteeringInput'] +1

        self.displayInputs()

        return self._data
        

        
        


        

    

        

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
        #update sliders
        self._parentWidget.widget.sliderThrottle.setValue(self._data['ThrottleInput'])
        self._parentWidget.widget.sliderSteering.setValue(self._data['SteeringInput'])
        self._parentWidget.widget.sliderBrake.setValue(self._data['BrakeInput'])

        #set values next to sliders:
        self._parentWidget.widget.lblThrottle.setText(str(self._data['ThrottleInput']))
        self._parentWidget.widget.lblSteering.setText(str(self._data['SteeringInput']))
        self._parentWidget.widget.lblBrake.setText(str(self._data['BrakeInput']))
        

    def setCurrentInput(self):
        self._parentWidget.widget.sliderThrottle.setEnabled(True)
        self._parentWidget.widget.sliderSteering.setEnabled(True)
        self._parentWidget.widget.sliderBrake.setEnabled(True)
        self.currentInput = 'Mouse'
        self.changeInputSource()
        
    def process(self):
        self._data['BrakeInput']    = self._parentWidget.widget.sliderBrake.value()
        self._data['ThrottleInput'] = self._parentWidget.widget.sliderThrottle.value()
        self._data['SteeringInput'] = self._parentWidget.widget.sliderSteering.value()
        self.displayInputs()
        

        return self._data