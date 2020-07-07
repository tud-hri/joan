from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction

from modules.joanmodules import JOANModules
from process.statesenum import State

class AgentmanagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction,  parent=None):
        super().__init__(module=JOANModules.AGENT_MANAGER, module_action=module_action, parent=parent)

        #initialize variables
        self.connected = False
        self.old_nr_cars = 0
        self.vehicles = []
        self.traffic_vehicles = []
        self.i = 1

        self.module_widget.btn_add_ego_agent.clicked.connect(self.add_ego_agent)
        self.module_widget.btn_add_traffic_agent.clicked.connect(self.add_traffic_agent)
        self.module_action.state_machine.add_state_change_listener(self._state_change_listener)

        self.module_widget.btnDisconnect.clicked.connect(self.disconnect)
        self.module_widget.groupVehicles.setEnabled(False)
        self.module_widget.btn_add_ego_agent.setEnabled(False)
        self.module_widget.btn_add_traffic_agent.setEnabled(False)
        self.module_widget.btnDisconnect.setEnabled(False)

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
            self.module_widget.btn_add_ego_agent.setEnabled(self.connected)
            self.module_widget.btn_add_traffic_agent.setEnabled(self.connected)
        elif self.module_action.state_machine.current_state == State.RUNNING:
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.btn_add_ego_agent.setEnabled(False)
            self.module_widget.btn_add_traffic_agent.setEnabled(False)
        elif self.module_action.state_machine.current_state == State.ERROR:
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.btn_add_ego_agent.setEnabled(False)
            self.module_widget.btn_add_traffic_agent.setEnabled(False)


        else:
            self.module_widget.btnDisconnect.setEnabled(False)
            #self.module_widget.groupVehicles.setEnabled(False)
            self.module_widget.btn_add_ego_agent.setEnabled(False)
            self.module_widget.btn_add_traffic_agent.setEnabled(False)

    def disconnect(self):
        """
        This function disconnects from carla, when it does it will also automatically destroy any cars that were spawned
        in the simulation.
        """
        self.connected = self.module_action.disconnect()
        self.module_widget.groupVehicles.setEnabled(self.connected)
        self.module_widget.btn_add_ego_agent.setEnabled(self.connected)
        self.module_widget.btn_add_traffic_agent.setEnabled(self.connected)
        self.module_widget.btnDisconnect.setEnabled(self.connected)
        for cars in self.vehicles:
            cars.remove_ego_agent()

    def add_ego_agent(self):
        self.vehicles = self.module_action.add_ego_agent()
        self.module_widget.layOut.insertWidget(len(self.vehicles)-1, self.vehicles[-1].vehicle_tab)

    def add_traffic_agent(self):
        self.traffic_vehicles = self.module_action.add_traffic_agent()
        self.module_widget.layOut.insertWidget(-1,self.traffic_vehicles[-1].vehicle_tab)

