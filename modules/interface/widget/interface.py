from process import Control
from PyQt5 import QtCore
import os

class InterfaceWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 20
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"interface.ui"))
        self.data = {}
        self.writeNews(channel=self, news=self.data)

        self.statehandler.stateChanged.connect(self.handlestate)

        pass
    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data = self.readNews('modules.feedbackcontroller.widget.feedbackcontroller.FeedbackcontrollerWidget')
        self.widget.lblStatusInterface.setText(str(self.data))
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
            self.widget.lblStatusInterface.setText(str(stateAsState))

        except Exception as inst:
            print (inst)
