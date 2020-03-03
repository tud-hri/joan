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
        self.millis = kwargs['millis']

        #self.statehandler.stateChanged.connect(self.finish)
        self.statehandler.stateChanged.connect(self.handlestate)
        self.ts = None
        self.te = None


    def do(self):
        self.counter += 1
        #print(" counter %d" % self.counter)
        if (self.counter == 500):
            self.statehandler.stateChanged.emit(self.statehandler.state)

            self.statehandler.requestStateChange(self.states.ERROR.INTERFACE.INIT_SIMENDO)
        self.widget.label_1.setText(str(self.counter))

    def show(self):
        self.startPulsar()

        self.widget.btnQuit.clicked.connect(self.finish)
        self.widget.show()
        self.ts = time.time()


    def finish(self):
        self.stopPulsar
        self.te = time.time()
        print('millis %d, counter %d,  time: %f ms, verhouding: %f ' % (self.millis, self.counter * self.millis, (self.te - self.ts) * 1000, (self.counter * self.millis) / ((self.te - self.ts) * 1000)))
        sleep(2)
        exit(0)

    def handlestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        print("gedaan", state, self.gui)
        #self.statehandler.stateChanged
        try:
            stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            
            # update the state label
            self.widget.lblState.setText(str(stateAsState))
        except Exception as inst:
            print (inst)

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