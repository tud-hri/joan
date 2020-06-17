from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction

from modules.joanmodules import JOANModules
from process.statesenum import State

class CarlainterfaceDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction,  parent=None):
        super().__init__(module=JOANModules.CARLA_INTERFACE, module_action=module_action, parent=parent)

        #initialize variables
        self.connected = False
        self.old_nr_cars = 0
        self.vehicles = []
        self.i = 1

        self.module_widget.spinVehicles.setRange(0, 5)
        self.module_widget.spinVehicles.lineEdit().setReadOnly(True)

        self.module_widget.spinVehicles.valueChanged.connect(lambda value: self.update_vehicles(value))
        self.module_action.state_machine.add_state_change_listener(self._state_change_listener)
        #self.module_action.hardware_manager_state_machine.add_state_change_listener(self._hardware_state_change_listener)

        self.module_widget.btnDisconnect.clicked.connect(self.disconnect)
        self.module_widget.groupVehicles.setEnabled(False)
        self.module_widget.spinVehicles.setEnabled(False)
        self.module_widget.btnDisconnect.setEnabled(False)

    def _hardware_state_change_listener(self):
        self._state_change_listener()

    def _state_change_listener(self):
        """"
        This function handles the enabling and disabling of the carla interface change
        """
        self.connected = self.module_action.check_connection()
        #link the spawning of vehicles to connected state
        #make sure you can only disconnect in the ready state
        if self.module_action.state_machine.current_state == State.READY:
            self.module_widget.btnDisconnect.setEnabled(True)
            self.module_widget.groupVehicles.setEnabled(self.connected)
            self.module_widget.spinVehicles.setEnabled(self.connected)
        elif self.module_action.state_machine.current_state == State.ERROR:
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.groupVehicles.setEnabled(False)
            self.module_widget.spinVehicles.setEnabled(False)
        else:
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.groupVehicles.setEnabled(False)
            self.module_widget.spinVehicles.setEnabled(False)

    def disconnect(self):
        """
        This function disconnects from carla, when it does it will also automatically destroy any cars that were spawned
        in the simulation.
        """
        self.connected = self.module_action.disconnect()
        self.module_widget.groupVehicles.setEnabled(self.connected)
        self.module_widget.spinVehicles.setEnabled(self.connected)
        self.module_widget.btnDisconnect.setEnabled(self.connected)
        for cars in self.vehicles:
            self.module_widget.layOut.removeWidget(cars.vehicle_tab)
            cars.vehicle_tab.setParent(None)
        self.module_widget.spinVehicles.setValue(0)

    def update_vehicles(self, value):
        """
        Adds new cars if you up the spinbox
        """
        if value < self.old_nr_cars and self.vehicles:
            self.module_widget.layOut.removeWidget(self.vehicles[-1].vehicle_tab)
            self.vehicles[-1].vehicle_tab.setParent(None)

        self.vehicles = self.module_action.update_cars(value)

        if value > self.old_nr_cars:
            self.module_widget.layOut.addWidget(self.vehicles[value-1].vehicle_tab)

        self.old_nr_cars = value
        