from process import Control
import os
from PyQt5 import QtCore
from time import sleep
import time

class MenuWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 20
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "menu.ui"))
        self.data = {}
        self.writeNews(channel=self, news=self.data)

        # self.widget = self.getGui()
        self.counter = 0

        # self.masterStateHandler.stateChanged.connect(self.finish)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)
        # self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        # self.ts = None
        # self.te = None
        self.millis = kwargs['millis']

        self.widget.btnQuit.clicked.connect(self._close)

    def do(self):
        self.counter += 1
        # print(" counter %d" % self.counter)
        # if (self.counter == 40):
        #    self.setInterval(1000)
        if (self.counter == 500):
            self.masterStateHandler.stateChanged.emit(self.masterStateHandler.state)

            self.masterStateHandler.requestStateChange(self.masterStates.ERROR)
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
        #self.ts = time.time()

    def _stop(self):
        self.stopPulsar()
        # if not self.ts:
        #    self.ts = time.time()
        #self.te = time.time()
        # try:
        #    print('millis %d, counter %d,  time: %f ms, verhouding: %f ' % (self.millis, self.counter * self.millis, (self.te - self.ts) * 1000, (self.counter * self.millis) / ((self.te - self.ts) * 1000)))
        # except Exception as inst:
        #    print(inst)

    def _close(self):
        self.widget.close()

    def handlemasterstate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        # self.masterStateHandler.stateChanged
        try:
            # stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.masterStateHandler.getState(state)  # ensure we have the State object (not the int)

            # emergency stop
            if stateAsState == self.masterStates.ERROR:
                self._stop()

            # update the state label
            self.widget.lblState.setText(str(stateAsState))
            self.widget.repaint()

        except Exception as inst:
            print(' in menu.py', inst)
    '''
    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        #self.masterStateHandler.stateChanged
        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.masterStateHandler.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.masterStates.ERROR:
                self._stop()

            # update the state label
            self.widget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print (' in menu.py' ,inst)
    '''
