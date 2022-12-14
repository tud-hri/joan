import time
import numpy as np
import pandas as pd
from os.path import exists

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from core.module_manager import ModuleManager
from core.statesenum import State
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from modules.joanmodules import JOANModules

import carla


class CarlaInterfaceManager(ModuleManager):
    """
    CarlaInterfaceManager module, inherits from the ModuleManager
    """

    def __init__(self, news, central_settings, signals, central_state_monitor, time_step_in_ms=10, parent=None):
        """
        :param news: contains all news from all modules
        :param signals: contains all signals
        :param time_step_in_ms: contains interval in ms
        :param parent: neede for Qt windows
        """
        super().__init__(module=JOANModules.CARLA_INTERFACE, news=news, central_settings=central_settings, signals=signals,
                         central_state_monitor=central_state_monitor, time_step_in_ms=time_step_in_ms, parent=parent)
        self._agent_settingdialogs_dict = {}
        self.central_settings = central_settings

        # CARLA connection variables:
        self.host = 'localhost'
        self.port = 2000
        self._world = None
        self.connected = False
        self.vehicle_tags = []
        self.spawn_points = []
        self.client = None
        self.world_map = None
        self._vehicle_bp_library = None
        self.carla_waypoints = None
        self.haptic_controllers = []
        self.signals = signals
        self.map_name = None

        self.connected = self.connect_carla()

        self.state_machine.set_transition_condition(State.STOPPED, State.INITIALIZED, self._check_controller_connections)
        self.state_machine.set_transition_condition(State.INITIALIZED, State.READY, self._check_connection)

    def _check_connection(self):
        return self.connected

    def _check_controller_connections(self):
        used_controllers = []
        for agent in self.module_settings.agents.values():
            if agent.agent_type is AgentTypes.NPC_VEHICLE:
                if agent.selected_npc_controller in used_controllers:
                    return False, 'Multiple NPC vehicle are connected to the same controller'
                else:
                    used_controllers.append(agent.selected_npc_controller)

        npc_controller_manager_settings = self.singleton_settings.get_settings(JOANModules.NPC_CONTROLLER_MANAGER)
        for controller in used_controllers:
            if controller not in npc_controller_manager_settings.controllers.keys():
                return False, 'An NPC vehicle is connected to a controller that does not exist'
        return True

    def initialize(self):
        """
        Initializes agents
        """
        super().initialize()
        for agent in self.module_settings.agents.values():
            self.shared_variables.agents[agent.identifier] = AgentTypes(agent.agent_type).shared_variables()

    def load_from_file(self, settings_file_to_load):
        """
        Loads all agent settings from file
        :param settings_file_to_load: filename for the settings
        """
        # remove all settings from the dialog
        for agent in self.module_settings.all_agents().values():
            self.remove_agent(agent.identifier)

        # load settings from file into module_settings object
        self.module_settings.load_from_file(settings_file_to_load)

        # add all settings tp module_dialog
        from_button = False
        for agent_settings in self.module_settings.all_agents().values():
            self.add_agent(AgentTypes(agent_settings.agent_type), from_button, agent_settings)

        self.module_dialog.update_dialog()

    def add_agent(self, agent_type: AgentTypes, from_button, agent_settings=None):
        """
        Add an agent
        :param agent_type: holds the agent type, see enum AgentTypes
        :param from_button: boolean to prevent showing more than one window
        :param agent_settings: contains settigns for added agent
        """
        # add to module_settings
        agent_settings = self.module_settings.add_agent(agent_type, agent_settings)

        # add to module_dialog
        self.module_dialog.add_agent(agent_settings, from_button)

    def remove_agent(self, identifier):
        """
        :param identifier: identifies an agent
        """
        # remove from settings
        self.module_settings.remove_agent(identifier)

        # remove settings from dialog
        self.module_dialog.remove_agent(identifier)

    def save_road(self, path):
        world_map = self._world.get_map()
        self.map_name = world_map.name.split('/')[-1]
        path_name = path + self.map_name + '.csv'
        if not exists(path_name):
            distance = 1.0
            waypoints = world_map.generate_waypoints(distance)
            lane = []
            x = []
            y = []
            yaw = []
            width = []

            for waypoint in waypoints:
                road_transform = waypoint.transform

                lane.append(waypoint.lane_id)
                x.append(road_transform.location.x)
                y.append(road_transform.location.y)
                yaw.append(road_transform.rotation.yaw)
                width.append(waypoint.lane_width)

            road = {'lane': lane, 'x': x, 'y': y, 'yaw': yaw, 'width': width}

            pd_road = pd.DataFrame(road)
            pd_road.to_csv(path_name)


    def connect_carla(self):
        """
        This function will try and connect to carla server if it is running in unreal
        If not a message box will pop up and the module will transition to error state.
        """
        if not self.connected:
            try:
                self.spawn_points.clear()
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.client = carla.Client(self.host, self.port)  # connecting to server
                self.client.set_timeout(2.0)
                time.sleep(2)  # wait for 2 seconds for the connection to establish

                # get world objects (vehicles and waypoints)
                self._world = self.client.get_world()
                self.save_road(path='trajectories\\')
                blueprint_library = self._world.get_blueprint_library()
                self._vehicle_bp_library = blueprint_library.filter('vehicle.*')
                for items in self._vehicle_bp_library:
                    self.vehicle_tags.append(items.id[8:])
                self.world_map = self._world.get_map()
                spawn_point_objects = self.world_map.get_spawn_points()
                for index, item in enumerate(spawn_point_objects):
                    self.spawn_points.append("Spawnpoint " + str(index))
                self.carla_waypoints = self.world_map.generate_waypoints(1.0)
                QApplication.restoreOverrideCursor()
                self.connected = True

                print('JOAN connected to CARLA Server!')

            except RuntimeError:
                msg_box = QtWidgets.QMessageBox()
                msg_box.setTextFormat(QtCore.Qt.RichText)

                QApplication.restoreOverrideCursor()
                msg_box.setText('Could not connect to CARLA. Check if CARLA is running in Unreal Engine')
                msg_box.exec()
                self.connected = False
                QApplication.restoreOverrideCursor()

        else:
            self.msg.setText('JOAN is already connected to CARLA')
            self.msg.exec()

        return self.connected

    def disconnect_carla(self):
        """
        This function will try and disconnect from the carla server, if the module was running it will transition into
        an error state
        """
        self.client = None
        self.connected = False

        return self.connected
