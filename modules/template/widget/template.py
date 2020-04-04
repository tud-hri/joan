from process import Control, State, translate
from PyQt5 import QtCore
from modules.template.action.states import TemplateStates
from modules.template.action.template import TemplateAction
import os

class TemplateWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 500
        kwargs['callback'] = [self.do]  # method will run each given millis
        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"template.ui"))
        
        self.data = {}
        self.writeNews(channel=self, news=self.data)

        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        self.defineModuleStateHandler(module=self, moduleStates=TemplateStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)
        
        # use Action with state handling, using only this widgets state changes
        try:
            self.action = TemplateAction()
        except Exception as inst:
            print('Exception in TemplateWidget', inst)

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
        self.window.show()
        print('in widget/template.py', self.moduleStateHandler)
        print('in widget/template.py', self.moduleStates)
        moduleStatesDict = self.moduleStates.getStates()
        for state in moduleStatesDict:
            print('in TemplateStates bij show', state, moduleStatesDict[state])


    def start(self):
        if not self.window.isVisible():
            self._show()
        print(self.widget.windowTitle())
        self.widget.setWindowTitle("Template title")
        self.moduleStateHandler.requestStateChange(self.moduleStates.TEMPLATE.RUNNING)
        self.startPulsar()

    def stop(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.TEMPLATE.STOPPED)
        self.stopPulsar()

    def _close(self):
        self.window.close()

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
                self._stop()

            # update the state label
            self.widget.lblState.setText(str(stateAsState))
            self.widget.repaint()

        except Exception as inst:
            print ('Exception in TemplateWidget', inst)

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.moduleStateHandler.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.stateWidget.lblModuleState.setText(str(stateAsState.name))
            self.window.repaint()

            if stateAsState == self.moduleStates.TEMPLATE.RUNNING:
                self.stateWidget.btnStart.setStyleSheet("background-color: green")
            else:
                self.stateWidget.btnStart.setStyleSheet("background-color: none")

        except Exception as inst:
            print (inst)
