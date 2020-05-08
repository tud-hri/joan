from process import Control, State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from PyQt5 import QtCore
from modules.joanmodules import JOANModules
from modules.carlainterface.action.states import CarlainterfaceStates
from modules.carlainterface.action.carlainterfaceaction import Carlavehicle
from modules.carlainterface.action.carlainterfaceaction import CarlainterfaceAction

import os

class CarlainterfaceDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(module=JOANModules.CARLA_INTERFACE, module_action=module_action, master_state_handler=master_state_handler, parent=parent)
        
        self.data = {}
        self._data_from_hardware = {}
        self.connected = False
        self.old_nr_cars = 0
        self.vehicles = []

        self.module_widget.spinVehicles.setRange(0, 5)
        self.module_widget.spinVehicles.lineEdit().setReadOnly(True)

        self.module_widget.spinVehicles.valueChanged.connect(lambda value: self.update_vehicles(value))
        self.module_widget.btnConnect.clicked.connect(self.connect)
        self.module_widget.btnDisconnect.clicked.connect(self.disconnect)
        self.module_widget.groupVehicles.setEnabled(False)
        self.module_widget.spinVehicles.setEnabled(False)
        self.module_widget.btnDisconnect.setEnabled(False)

    def connect(self):
        self.connected = self.module_action.connect()
        self.module_widget.groupVehicles.setEnabled(self.connected)
        self.module_widget.spinVehicles.setEnabled(self.connected)
        self.module_widget.btnConnect.setEnabled(not self.connected)
        self.module_widget.btnDisconnect.setEnabled(self.connected)

    def disconnect(self):
        self.connected = self.module_action.disconnect()
        self.module_widget.groupVehicles.setEnabled(self.connected)
        self.module_widget.spinVehicles.setEnabled(self.connected)
        self.module_widget.btnDisconnect.setEnabled(self.connected)
        self.module_widget.btnConnect.setEnabled(not self.connected)
        for cars in self.vehicles:
            self.module_widget.layOut.removeWidget(cars.vehicle_tab)
            cars.vehicle_tab.setParent(None)
        self.module_widget.spinVehicles.setValue(0)
        

    
    def update_vehicles(self, value):
        if value < self.old_nr_cars and self.vehicles:
            self.module_widget.layOut.removeWidget(self.vehicles[-1].vehicle_tab)
            self.vehicles[-1].vehicle_tab.setParent(None)

        self.vehicles = self.module_action.update_cars(value)

        if value > self.old_nr_cars:
            self.module_widget.layOut.addWidget(self.vehicles[value-1].vehicle_tab)

        self.old_nr_cars = value
        