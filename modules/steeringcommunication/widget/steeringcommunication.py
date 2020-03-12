from process import Control
from PyQt5 import QtCore
import os
from modules.steeringcommunication import SteeringcommunicationAction
#from steeringcommunication import SteeringcommunicationAction

class SteeringcommunicationWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = [self.do]  # method will run each given millis

        kwargs['ui'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),"steeringcommunication.ui")
        Control.__init__(self, *args, **kwargs)

        self.statehandler.stateChanged.connect(self.handlestate)
        try:
            self.action = SteeringcommunicationAction()
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)
        self.i = 0

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.i  = self.i + 1

        if(self.statehandler._state is self.states.STEERINGWHEEL.ON):
            print(self.statehandler._state)
            print(self.i)
        pass

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.widget.show()
        self.widget.btnInitialize.clicked.connect(self.action.initialize)
        self.widget.btnStart.clicked.connect(self.action.start)
        self.widget.btnStop.clicked.connect(self.action.stop)
        self.action.initialize()
        

    def start(self):
        if not self.widget.isVisible():
            self._show()
        self.startPulsar()

    def stop(self):
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
            
            # Start if the system is initialized
            if stateAsState == self.states.STEERINGWHEEL.INITIALIZED:
                self.start()

            # Reinitialize available if exception
            if stateAsState == self.states.STEERINGWHEEL.ERROR.INIT:
                self.widget.btnInitialize.setEnabled(True)
            else:
                self.widget.btnInitialize.setEnabled(False)


            # emergency stop
            if stateAsState == self.states.ERROR:
                self.stop()

            # update the state label
            self.widget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print (inst)
