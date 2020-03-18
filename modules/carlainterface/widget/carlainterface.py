from process import Control, State, translate
from PyQt5 import QtCore
import os
from modules.carlainterface.action.carlainterface import Carlacommunication

class CarlainterfaceWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 50
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"carlainterface.ui"))
        
        self.data = {}
        self.writeNews(channel=self, news=self.data)
        self.counter = 0

        self.statehandler.stateChanged.connect(self.handlestate)

        self.widget.btnStart.clicked.connect(self.start)
        self.widget.btnStop.clicked.connect(self.stop)

    
    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data = self.Carlacomm.getData()
        self.writeNews(channel=self, news=self.data)

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.Carlacomm = Carlacommunication()
        self.widget.show()
        #Carlacommunication.print(self)

    def start(self):
        if not self.widget.isVisible():
            self._show()
        #Connect to the server
        self.Carlacomm.start()
        self.startPulsar()

    def stop(self):
        self.Carlacomm.stop()
        self.stopPulsar()

    def _close(self):
        self.stopPulsar()
        del self.Carlacomm
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
            self.widget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print (inst)
