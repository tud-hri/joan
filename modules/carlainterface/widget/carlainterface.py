import os
from modules.carlainterface.action.states import CarlainterfaceStates
from modules.carlainterface.action.carlainterface import Carlacommunication
from modules.carlainterface.action.carlainterface import Carlavehicle

from process import Control, State, translate
from PyQt5 import QtCore

class CarlainterfaceWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 2
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterfaceWidget.ui"))

        self.data = {}
        self.data['vehicles'] = None
        self._data_from_hardware = {}
        self.writeNews(channel=self, news=self.data)
        self.is_connected = False

        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        self.defineModuleStateHandler(module=self, moduleStates=CarlainterfaceStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)

        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION)
        self.widget.spinVehicles.setRange(0, 5)
        self.widget.spinVehicles.lineEdit().setReadOnly(True)

        self.widget.spinVehicles.valueChanged.connect(self.update_cars)
        self.widget.btnConnect.clicked.connect(self.connect)
        self.widget.groupVehicles.setEnabled(False)
        self.widget.spinVehicles.setEnabled(False)

        self.vehicles = []

        self.carlaCommunication = Carlacommunication(self)

    def connect(self):
        self.is_connected = self.carlaCommunication.connect()
        self.widget.groupVehicles.setEnabled(self.is_connected)
        self.widget.spinVehicles.setEnabled(self.is_connected)
        self.widget.btnConnect.setEnabled(not self.is_connected)
        self.do()

    def update_cars(self):
        # Delete excess vehicles if any
        while self.widget.spinVehicles.value() < len(self.vehicles):
            self.vehicles[-1].destroyTab()
            self.vehicles.pop(-1)

        # Create new vehicles and show them:
        for i in range(len(self.vehicles), self.widget.spinVehicles.value()):
            self.vehicles.append(Carlavehicle(self, i))

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data['vehicles'] = self.vehicles
        self.writeNews(channel=self, news=self.data)

        print(self.data)

        self._data_from_hardware = self.readNews('modules.hardwarecommunication.widget.hardwarecommunication.HardwarecommunicationWidget')
        try:
            for items in self.vehicles:
                if items.spawned:
                    items.applycontrol(self._data_from_hardware)
        except Exception as inst:
            print('Could not apply control', inst)

   
        

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        try:
            self.window.show()
        except Exception as e:
            print(' ############## Exception was: #########', e)

    def start(self):
        """
        Starts the pulsar and requests appropriate module state change
        """
        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION.RUNNING)
        self.startPulsar()

    def stop(self):
        """
        Stops the pulsar and requests appropriate module state change
        """
        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION.STOPPED)
        self.stopPulsar()

    def _close(self):
        """
        Closes the window and requests appropriate module state change
        """
        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION.STOPPED)
        self.window.close()

    def handlemasterstate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            stateAsState = self.masterStateHandler.getState(state)  # ensure we have the State object (not the int)

            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.stateWidget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print(inst)

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            # stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.moduleStateHandler.getState(state)  # ensure we have the State object (not the int)]
            self.writeNews(channel=self, news=self.data)

            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.stateWidget.lblModuleState.setText(str(stateAsState.name))

            if stateAsState == self.moduleStates.SIMULATION.RUNNING:
                self.stateWidget.btnStart.setStyleSheet("background-color: green")
            else:
                self.stateWidget.btnStart.setStyleSheet("background-color: none")

        except Exception as inst:
            print(inst)
