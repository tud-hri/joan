from process import Control, State, translate
from PyQt5 import QtCore
import os
from modules.siminterface.action.siminterface import Simcommunication

class SiminterfaceWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 500
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"siminterface.ui"))
        
        self.data = {}
        self.writeNews(channel=self, news=self.data)
        self.counter = 0

        self.masterStateHandler.stateChanged.connect(self.handlestate)

        self.widget.btnStart.clicked.connect(self._start)
        self.widget.btnStop.clicked.connect(self._stop)

        try:
            self.action = Simcommunication()
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)

    
    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data = self.action.getData()
        self.writeNews(channel=self, news=self.data)

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        # self.action = Simcommunication() # @ JORIS: ik denk dat je dit in the init moet zetten; stel dat je nu op close drukt voor deze widget voordat je op open klikt, dan loopt ie vast. 
        self.widget.show()

    def _start(self):
        if not self.widget.isVisible():
            self._show()
        #Connect to the server
        self.action.start()
        self.startPulsar()

    def _stop(self):
        self.action.stop()
        self.stopPulsar()

    def _close(self):
        self.action.stop()
        self.stopPulsar()
        del self.action
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
            self.widget.lblMasterstate.setText(str(stateAsState))

        except Exception as inst:
            print (inst)
