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
        self.data['Theta'] = 'hey hallo'
        self.data['ThetaDot'] = 0
        self.writeNews(channel=self, news=self.data)
        self.counter = 0

        self.statehandler.stateChanged.connect(self.handlestate)

        self.newtab = uic.loadUi(uifile = os.path.join(os.path.dirname(os.path.realpath(__file__)),"basic.ui"))
        self.widget.tabWidget.addTab(self.newtab,'hai')
        Manual = Manualcontrol(self)

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.counter = self.counter + 1
        self.data['Theta'] = 'waddup'
        #self.data['ThetaDot'] = self.data['Theta'] + self.counter
        self.writeNews(channel=self, news= self.data)
        #print(self.counter)

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
