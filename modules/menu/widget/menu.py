from process import Control
import os
from PyQt5 import QtCore
from time import sleep
import time

class MenuWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 20
        kwargs['callback'] = [self.do]  # method will run each given millis

        kwargs['ui'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),"menu.ui")
        Control.__init__(self, *args, **kwargs)

        #self.widget = self.getGui()
        self.counter = 0

        #self.statehandler.stateChanged.connect(self.finish)
        self.statehandler.stateChanged.connect(self.handlestate)
        self.ts = None
        self.te = None
        self.millis = kwargs['millis']

    def do(self):
        self.counter += 1
        #print(" counter %d" % self.counter)
        #if (self.counter == 40):
        #    self.setInterval(1000)
        if (self.counter == 500):
            self.statehandler.stateChanged.emit(self.statehandler.state)

            self.statehandler.requestStateChange(self.states.ERROR)
        self.widget.label_1.setText(str(self.counter))

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            self.millis = int(millis)
            self.setInterval(self.millis)
        except:
            pass

    def _show(self):
        self.widget.show()

    def _start(self):
        if not self.widget.isVisible():
            self._show()
        self.startPulsar()
        self.widget.btnQuit.clicked.connect(self.laatguidictzien)
        self.ts = time.time()


    def _stop(self):
        self.stopPulsar()
        if not self.ts:
            self.ts = time.time()
        self.te = time.time()
        try:
            print('millis %d, counter %d,  time: %f ms, verhouding: %f ' % (self.millis, self.counter * self.millis, (self.te - self.ts) * 1000, (self.counter * self.millis) / ((self.te - self.ts) * 1000)))
        except Exception as inst:
            print(inst)
    
    def _close(self):
        self.widget.close()

    def handlestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        print("gedaan in menu", state, self.gui)
        #self.statehandler.stateChanged
        try:
            stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.states.ERROR:
                self.stop()

            # update the state label
            self.widget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print (' in menu.py' ,inst)

    def laatguidictzien(self):
        print ('      guiDict in menu.py       ', self.getAllGui())

        '''
        menuWidget = self.menuWindow.getGui()
        menuWidget.btnQuit.clicked.connect(app.quit)
        h3 = HapticTrainer(gui=menuWidget)


        h3.statehandler.stateChanged.connect(stateChanged)
        print (h3.statehandler.state)
        h3.statehandler.stateChanged.emit(h3.statehandler.state)
        print (h3.statehandler.requestStateChange(h3.statehandler.state))


        menuWidget.show()
        '''