from process import Control, State, translate
from PyQt5 import QtCore
import os

class TemplateWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 20
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"template.ui"))
        self.data = {}
        self.writeNews(channel=self, news=self.data)

        self.statehandler.stateChanged.connect(self.handlestate)
        
            # SensoDrive states
        self.states.STEERINGWHEEL                   = State(200, translate('SteeringwheelState', 'Steering wheel State'), -1,150)
        self.states.STEERINGWHEEL.OFF               = State(201, translate('SteeringwheelState', 'Steeringwheel Off'), -1,150, 202, 204,2040)
        self.states.STEERINGWHEEL.READY             = State(202, translate('SteeringwheelState', 'Steeringwheel Ready'), -1,150, 201, 203,204)
        self.states.STEERINGWHEEL.ON                = State(203, translate('SteeringwheelState', 'Steeringwheel On'), -1,150, 202, 204)
        self.states.STEERINGWHEEL.ERROR             = State(204, translate('SteeringwheelState', 'Steeringhweel Error'), -1, 150, 201)
        self.states.STEERINGWHEEL.ERROR.INIT        = State(2040, translate('SteeringwheelState', 'Steeringhweel Error'), -1, 150, 201)
        self.states.STEERINGWHEEL.INITIALIZED       = State(205, translate('SteeringwheelState', 'Steeringhweel Error'), -1, 150, 201, 202, 203, 204,2040)


    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
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

    def _start(self):
        if not self.widget.isVisible():
            self._show()
        print(self.widget.windowTitle())
        self.widget.setWindowTitle("Template title")
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
            self.widget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print (inst)
