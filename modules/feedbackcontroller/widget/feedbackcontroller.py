from process import Control, State, translate
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QWidget
import os
from modules.feedbackcontroller.action.feedbackcontroller import *

class FeedbackcontrollerWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 500
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"feedbackcontroller.ui"))
        
        self.data = {}
        self.writeNews(channel=self, news=self.data)
        self.counter = 0

        self.statehandler.stateChanged.connect(self.handlestate)
        
        # Initiate the different classes (controllers) you want:
        self._controller = Basecontroller()
        #self.FDCA = FDCAControl(self)
        #self._controller = Manualcontrol(self)

        self.Controllers =  [Manualcontrol(self), FDCAcontrol(self)]
        
        

        self.widget.tabWidget.currentChanged.connect(self.changedControl)




    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data = self._controller.process()
        self.writeNews(channel=self, news= self.data)
        print('FeedbackcontrollerTick')

    def process(self):
        "Hier kijken welke tab is geselecteerd en dan de juiste Process methode van de controller klasse pakken"
        #self.data = self._controller.process
    
    def changedControl(self):
        self._controller = self.Controllers[self.widget.tabWidget.currentIndex()]
        print('control changed!')

        
    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.widget.show()
        #self.statehandler.requestStateChange(self.states.FEEDBACKCONTROLLER)
        

    def _start(self):
        if not self.widget.isVisible():
            self._show()
        print(self.widget.windowTitle())
        self.startPulsar()
        

    def _stop(self):
        self.stopPulsar()

    def _close(self):
        self.widget.close()

    def printshit(self):
        print('shit')

    def handlestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.states.ERROR:
                self._stop()

            # update the state label
            self.widget.lblState.setText(stateAsState.name)

        except Exception as inst:
            print (inst)
