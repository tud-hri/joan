from process import Control
from PyQt5 import QtCore
import os
from modules.steeringcommunication.action.states import SteeringcommunicationStates
from modules.steeringcommunication.action.steeringcommunication import SteeringcommunicationAction

class SteeringcommunicationWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"steeringcommunication.ui"))
        self.data = {}
        self.data['throttle'] = 0
        self.data['damping'] = 0
        self.writeNews(channel=self, news=self.data)

        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        self.defineModuleStateHandler(module=self, moduleStates=SteeringcommunicationStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)

        try:
            self.action = SteeringcommunicationAction()
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)
        self.i = 0

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.i  = self.i + 1

        self.data['throttle'] = self.i
        self.data['damping'] = 0
        self.writeNews(channel=self, news=self.data)

        if(self.moduleStateHandler._state is self.moduleStates.STEERINGWHEEL.ON):
            print(self.masterStateHandler._state)
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

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.moduleStateHandler.getState(state) # ensure we have the State object (not the int)
            
            # Start if the system is initialized
            if stateAsState == self.moduleStates.STEERINGWHEEL.INITIALIZED:
                self.start()

            # Reinitialize available if exception
            if stateAsState == self.moduleStates.STEERINGWHEEL.ERROR.INIT:
                self.widget.btnInitialize.setEnabled(True)
            else:
                self.widget.btnInitialize.setEnabled(False)


            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self.stop()

            # update the state label
            self.widget.lblState.setText(stateAsState.name)

        except Exception as inst:
            print (inst)

    def handlemasterstate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.masterStateHandler.getState(state) # ensure we have the State object (not the int)
            
           # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self.stop()

            # update the state label
            self.widget.lblState.setText(stateAsState.name)

        except Exception as inst:
            print (inst)
