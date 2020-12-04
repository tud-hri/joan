import glob
import os
import sys
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QApplication

from core.module_manager import ModuleManager
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from modules.joanmodules import JOANModules

msg_box = QMessageBox()
msg_box.setTextFormat(QtCore.Qt.RichText)

try:
    sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    import carla

except IndexError:
    msg_box.setText("""
                <h3> Could not find the carla python API! </h3>
                <h3> Check whether you copied the egg file correctly, reference:
            <a href=\"https://joan.readthedocs.io/en/latest/setup-run-joan/#getting-necessary-python3-libraries-to-run-joan\">https://joan.readthedocs.io/en/latest/setup-run-joan/#getting-necessary-python3-libraries-to-run-joan</a>
            </h3>
            """)
    msg_box.exec()
    pass


class CarlaInterfaceManager(ModuleManager):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """

    def __init__(self, news, signals, time_step_in_ms=10, parent=None):
        """

        :param news:
        :param signals:
        :param time_step_in_ms:
        :param parent:
        """
        super().__init__(module=JOANModules.CARLA_INTERFACE, news=news, signals=signals, time_step_in_ms=time_step_in_ms, parent=parent)
        self._agent_settingdialogs_dict = {}

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

        self.connected = self.connect_carla()

    def initialize(self):
        """

        :return:
        """
        super().initialize()
        for agent in self.module_settings.agents.values():
            self.shared_variables.agents[agent.identifier] = AgentTypes(agent.agent_type).shared_variables()

    def load_from_file(self, settings_file_to_load):
        """

        :param settings_file_to_load:
        :return:
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

    def add_agent(self, agent_type: AgentTypes, from_button, agent_settings=None):
        """
        Add an agent
        :param agent_type:
        :param from_button:
        :param agent_settings:
        :return:
        """
        # add to module_settings
        agent_settings = self.module_settings.add_agent(agent_type, agent_settings)

        # add to module_dialog
        self.module_dialog.add_agent(agent_settings, from_button)

    def remove_agent(self, identifier):
        """

        :param identifier:
        :return:
        """
        # remove from settings
        self.module_settings.remove_agent(identifier)

        # remove settings from dialog
        self.module_dialog.remove_agent(identifier)

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
                time.sleep(2)
                self._world = self.client.get_world()  # get world object (contains everything)
                blueprint_library = self._world.get_blueprint_library()
                self._vehicle_bp_library = blueprint_library.filter('vehicle.*')
                for items in self._vehicle_bp_library:
                    self.vehicle_tags.append(items.id[8:])
                self.world_map = self._world.get_map()
                spawn_point_objects = self.world_map.get_spawn_points()
                for item in spawn_point_objects:
                    self.spawn_points.append("Spawnpoint " + str(spawn_point_objects.index(item)))
                self.carla_waypoints = self.world_map.generate_waypoints(0.5)
                QApplication.restoreOverrideCursor()
                self.connected = True

                print('JOAN connected to CARLA Server!')

            except RuntimeError:
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

    def _open_settings_dialog(self, agent_name):
        """

        :param agent_name:
        :return:
        """
        self._agent_settingdialogs_dict[agent_name].show()
        self._get_update_from_other_modules(agent_name)
