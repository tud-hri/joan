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
        self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterface.ui"))

        self.data = {}
        self.data['vehicles'] = None
        self._data_from_hardware = {}
        self.write_news(channel=self, news=self.data)
        self.is_connected = False

        # creating a self.module_state_handler which also has the module_states in self.module_state_handler.states
        self.define_module_state_handler(module=self, module_states=CarlainterfaceStates())
        self.module_state_handler.state_changed.connect(self.handle_module_state)
        self.master_state_handler.state_changed.connect(self.handle_master_state)

        self.module_state_handler.request_state_change(self.module_states.SIMULATION)
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
            self.vehicles[-1].destroy_tab()
            self.vehicles.pop(-1)

        # Create new vehicles and show them:
        for i in range(len(self.vehicles), self.widget.spinVehicles.value()):
            self.vehicles.append(Carlavehicle(self, i))

    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data['vehicles'] = self.vehicles
        self.write_news(channel=self, news=self.data)

        self._data_from_hardware = self.read_news('modules.hardwaremanager.widget.hardwaremanager.HardwaremanagerWidget')
        try:
            for items in self.vehicles:
                if items.spawned:
                    items.apply_control(self._data_from_hardware)
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
        self.module_state_handler.request_state_change(self.module_states.SIMULATION.RUNNING)
        self.startPulsar()

    def stop(self):
        """
        Stops the pulsar and requests appropriate module state change
        """
        self.module_state_handler.request_state_change(self.module_states.SIMULATION.STOPPED)
        self.stopPulsar()

    def _close(self):
        """
        Closes the window and requests appropriate module state change
        """
        self.module_state_handler.request_state_change(self.module_states.SIMULATION.STOPPED)
        self.window.close()

    def handle_master_state(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            state_as_state = self.master_state_handler.get_state(state)  # ensure we have the State object (not the int)

            # emergency stop
            if state_as_state == self.module_states.ERROR:
                self._stop()

            # update the state label
            self.state_widget.lbl_state.setText(str(state_as_state))

        except Exception as inst:
            print(inst)

    def handle_module_state(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            # state_as_state = self.states.get_state(state) # ensure we have the State object (not the int)
            state_as_state = self.module_state_handler.get_state(state)  # ensure we have the State object (not the int)]
            self.write_news(channel=self, news=self.data)

            # emergency stop
            if state_as_state == self.module_states.ERROR:
                self._stop()

            # update the state label
            self.state_widget.lbl_module_state.setText(str(state_as_state.name))

            if state_as_state == self.module_states.SIMULATION.RUNNING:
                self.state_widget.btn_start.setStyleSheet("background-color: green")
            else:
                self.state_widget.btn_start.setStyleSheet("background-color: none")

        except Exception as inst:
            print(inst)
