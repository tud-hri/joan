from process import Control, State, translate
from PyQt5 import QtCore, uic
from modules.hardwarecommunication.action.states import HardwarecommunicationStates
from modules.hardwarecommunication.action.hardwarecommunication import HardwarecommunicationAction, BaseInput
import os

class HardwarecommunicationWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 2
        kwargs['callback'] = [self.do]  # method will run each given millis
        Control.__init__(self, *args, **kwargs)
        
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremanager_ui.ui"))
        self._input_data = {}
        self._inputlist = {}
        self.counter = 0
        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        self.defineModuleStateHandler(module=self, moduleStates=HardwarecommunicationStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)
        
        # use Action with state handling, using only this widgets state changes
        try:
            self.action = HardwarecommunicationAction()
            self.action.widget = self
        except Exception as inst:
            print(inst)
        
        self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/inputtype_ui.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.action.selected_input)
        self.widget.btn_add_hardware.clicked.connect(self._input_type_dialog.show)

        self._inputlist = self.action.input_devices_classes

        self._input = BaseInput(self, self.action)
        

        self.writeNews(channel=self, news=self._input_data)

        self.installEventFilter(self)

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        for key in self._inputlist:
            self._input_data[key] = self._inputlist[key].process()


    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.window.show()
        moduleStatesDict = self.moduleStates.getStates()
        for state in moduleStatesDict:
            print('in HardwarecommunicationStates bij show', state, moduleStatesDict[state])


    def start(self):
        if not self.window.isVisible():
            self._show()
        self.moduleStateHandler.requestStateChange(self.moduleStates.HARDWARECOMMUNICATION.RUNNING)
        self.startPulsar()

    def stop(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.HARDWARECOMMUNICATION.STOPPED)
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
            print (inst)

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
            self.stateWidget.repaint()

            if stateAsState == self.moduleStates.HARDWARECOMMUNICATION.RUNNING:
                self.stateWidget.btnStart.setStyleSheet("background-color: green")
            else:
                self.stateWidget.btnStart.setStyleSheet("background-color: none")

        except Exception as inst:
            print (inst)
