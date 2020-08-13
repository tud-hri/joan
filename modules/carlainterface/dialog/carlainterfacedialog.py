from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog
from process.statesenum import State


class CarlaInterfaceDialog(JoanModuleDialog):
    """
    This class is the actual dialog you see when you open up the module. Mostly this class serves as a
    connection between the user and the 'brains', which is the action module.
    """

    def __init__(self, module_action: JoanModuleAction, parent=None):
        """
        Initializes the class
        :param module_action:
        :param parent:
        """
        super().__init__(module=JOANModules.CARLA_INTERFACE, module_action=module_action, parent=parent)

        # initialize variables
        self.connected = False
        self.old_nr_cars = 0
        self.i = 1

        self.module_widget.btn_add_ego_agent.clicked.connect(self.add_ego_agent)
        self.module_widget.btn_add_traffic_agent.clicked.connect(self.add_traffic_agent)
        self.module_action.state_machine.add_state_change_listener(self._state_change_listener)
        self.module_widget.btn_spawn_all.clicked.connect(self._spawn_all)
        self.module_widget.btn_destroy_all.clicked.connect(self._destroy_all)
        self.module_widget.btn_remove_all.clicked.connect(self._remove_all)

        self.module_widget.btnDisconnect.clicked.connect(self.disconnect)
        self.module_widget.groupVehicles.setEnabled(False)
        self.module_widget.btn_add_ego_agent.setEnabled(False)
        self.module_widget.btn_add_traffic_agent.setEnabled(False)
        self.module_widget.btnDisconnect.setEnabled(False)
        self.module_widget.btn_spawn_all.setEnabled(False)
        self.module_widget.btn_destroy_all.setEnabled(False)
        self.module_widget.btn_remove_all.setEnabled(False)

        # Settings
        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.load_settings.setEnabled(False)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)
        # self.initialize_widgets_from_settings()

    def _state_change_listener(self):
        """"
        This function handles the enabling and disabling of the carla interface change
        """
        self.connected = self.module_action.check_connection()
        # link the spawning of vehicles to connected state
        # make sure you can only disconnect in the ready state
        if self.module_action.state_machine.current_state == State.READY:
            self.load_settings.setEnabled(self.connected)
            self.module_widget.btnDisconnect.setEnabled(True)
            self.module_widget.groupVehicles.setEnabled(self.connected)
            self.module_widget.btn_add_ego_agent.setEnabled(self.connected)
            self.module_widget.btn_add_traffic_agent.setEnabled(self.connected)
            self.module_widget.btn_spawn_all.setEnabled(self.connected)
            self.module_widget.btn_destroy_all.setEnabled(self.connected)
            self.module_widget.btn_remove_all.setEnabled(self.connected)
        elif self.module_action.state_machine.current_state == State.RUNNING:
            self.load_settings.setEnabled(False)
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.btn_add_ego_agent.setEnabled(False)
            self.module_widget.btn_add_traffic_agent.setEnabled(False)
            self.module_widget.btn_spawn_all.setEnabled(False)
            self.module_widget.btn_destroy_all.setEnabled(False)
            self.module_widget.btn_remove_all.setEnabled(False)
        elif self.module_action.state_machine.current_state == State.ERROR:
            self.load_settings.setEnabled(False)
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.btn_add_ego_agent.setEnabled(False)
            self.module_widget.btn_add_traffic_agent.setEnabled(False)
            self.module_widget.btn_spawn_all.setEnabled(False)
            self.module_widget.btn_destroy_all.setEnabled(False)
            self.module_widget.btn_remove_all.setEnabled(False)


        else:
            self.load_settings.setEnabled(False)
            self.module_widget.btnDisconnect.setEnabled(False)
            # self.module_widget.groupVehicles.setEnabled(False)
            self.module_widget.btn_add_ego_agent.setEnabled(False)
            self.module_widget.btn_add_traffic_agent.setEnabled(False)
            self.module_widget.btn_spawn_all.setEnabled(False)
            self.module_widget.btn_destroy_all.setEnabled(False)
            self.module_widget.btn_remove_all.setEnabled(False)

    def _load_settings(self):
        """
        Loads settings from json file
        :return:
        """
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings', filter='*.json')
        if settings_file_to_load:

            # remove all current agents  first
            while self.module_action.vehicles:
                self.module_action.vehicles[-1].remove_ego_agent()

            while self.module_action.traffic_vehicles:
                self.module_action.traffic_vehicles[-1].remove_traffic_agent()

            self.module_action.load_settings_from_file(settings_file_to_load)
            self.initialize_widgets_from_settings()

    def _save_settings(self):
        """
        Saves settings to json file
        :return:
        """
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings', filter='*.json')
        if file_to_save_in:
            self.module_action.save_settings_to_file(file_to_save_in)

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
        for cars in self.module_action.vehicles:
            cars.remove_ego_agent()

    def add_ego_agent(self):
        """
        Adds an ego agent (in this case a vehicle a user can control)
        :return:
        """
        self.module_action.vehicles = self.module_action.add_ego_agent()
        self.module_action.vehicles[-1].settings_dialog.show()
        self.module_widget.layOut.insertWidget(len(self.module_action.vehicles) - 1,
                                               self.module_action.vehicles[-1].vehicle_tab)

    def add_traffic_agent(self):
        """
        Adds a traffic agent
        :return:
        """
        self.module_action.traffic_vehicles = self.module_action.add_traffic_agent()
        self.module_action.traffic_vehicles[-1].settings_dialog.show()
        self.module_widget.layOut.insertWidget(-1, self.module_action.traffic_vehicles[-1].vehicle_tab)

    def initialize_widgets_from_settings(self):
        """
        If settings are loaded from a json file this function will add the appropariate widgets.
        :return:
        """
        for ego_agent_settings in self.module_action.settings.ego_vehicles:
            self.module_action.vehicles = self.module_action.add_ego_agent(ego_agent_settings)
            self.module_widget.layOut.insertWidget(len(self.module_action.vehicles) - 1,
                                                   self.module_action.vehicles[-1].vehicle_tab)

        for traffic_agent_settings in self.module_action.settings.traffic_vehicles:
            self.module_action.traffic_vehicles = self.module_action.add_traffic_agent(traffic_agent_settings)
            self.module_action.traffic_vehicles[-1].load_trajectory()
            self.module_widget.layOut.insertWidget(-1, self.module_action.traffic_vehicles[-1].vehicle_tab)

    def _remove_all(self):
        """
        Removes all agents from the module
        :return:
        """
        while self.module_action.vehicles:
            self.module_action.vehicles[-1].remove_ego_agent()

        while self.module_action.traffic_vehicles:
            self.module_action.traffic_vehicles[-1].remove_traffic_agent()

    def _spawn_all(self):
        """
        Spawns all loaded agents in the simulation
        :return:
        """
        for agents in self.module_action.vehicles:
            agents.spawn_car()
        for traffic_agents in self.module_action.traffic_vehicles:
            traffic_agents.spawn_car()

    def _destroy_all(self):
        """
        Destroys all agents currently in simulation
        :return:
        """
        for agents in self.module_action.vehicles:
            agents.destroy_car()
        for traffic_agents in self.module_action.traffic_vehicles:
            traffic_agents.destroy_car()
