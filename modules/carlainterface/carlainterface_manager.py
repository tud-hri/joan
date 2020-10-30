from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import Qt

import sys, os, glob
import time

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

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.CARLA_INTERFACE, time_step_in_ms=time_step_in_ms, parent=parent)
        self._agent_settingdialogs_dict = {}
        # CARLA connection variables:
        self.host = 'localhost'
        self.port = 2000
        self._world = None
        self.connected = False
        self.vehicle_tags = []
        self.spawn_points = []


        self.connected = self.connect_carla()

    def initialize(self):
        super().initialize()
        for egovehicle in self.module_settings.ego_vehicles.values():
            self.shared_variables.ego_vehicles[egovehicle.identifier] = egovehicle.input_type.shared_variables()

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
                world_map = self._world.get_map()
                spawn_point_objects = world_map.get_spawn_points()
                for item in spawn_point_objects:
                    self.spawn_points.append("Spawnpoint " + str(spawn_point_objects.index(item)))
                self.carla_waypoints = world_map.generate_waypoints(0.5)
                print('JOAN connected to CARLA Server!')
                QApplication.restoreOverrideCursor()
                self.connected = True

                # # TODO: untested, settings are only able to be applied after connecting to CARLA
                # self.apply_loaded_settings()

            except RuntimeError as inst:
                QApplication.restoreOverrideCursor()
                msg_box.setText('Could not connect check if CARLA is running in Unreal')
                msg_box.exec()
                self.connected = False
                QApplication.restoreOverrideCursor()

        else:
            self.msg.setText('Already Connected')
            self.msg.exec()

        return self.connected


    def _open_settings_dialog(self, agent_name):
        self._agent_settingdialogs_dict[agent_name].show()
        self._get_update_from_other_modules(agent_name)

    def _add_agent(self, agent_type, agent_settings=None):
        """
        Add hardware agent
        :param agent_type:
        :param agent_settings:
        :return:
        """
        if not agent_settings:
            agent_settings = agent_type.settings(agent_type)

            # find unique identifier
            type_dict = None
            if agent_type == AgentTypes.EGO_VEHICLE:
                type_dict = self.module_settings.ego_vehicles

            identifier = 0
            for v in type_dict.values():
                if v.identifier > identifier:
                    identifier = v.identifier
            agent_settings.identifier = identifier + 1

        # check if settings do not already exist
        if agent_type == AgentTypes.EGO_VEHICLE:
            if agent_settings not in self.module_settings.ego_vehicles.values():
                self.module_settings.ego_vehicles[agent_settings.identifier] = agent_settings

        # create dialog thing
        agent_name = '{0!s} {1!s}'.format(agent_type, str(agent_settings.identifier))

        # link buttons within settings dialog:
        self._agent_settingdialogs_dict[agent_name] = agent_type.klass_dialog(agent_settings)
        self._agent_settingdialogs_dict[agent_name].btn_update.clicked.connect(lambda: self._get_update_from_other_modules(agent_name))
        return agent_name

    def _remove_agent(self, agent_name):
        # Remove settings if they are available
        settings_object = None

        if 'Ego Vehicle' in agent_name:
            identifier = int(agent_name.replace('Ego Vehicle', ''))
            for egovehicle in self.module_settings.ego_vehicles.values():
                if egovehicle.identifier == identifier:
                    settings_object = egovehicle

        self.module_settings.remove_agent(settings_object)

        # Remove settings dialog
        self._agent_settingdialogs_dict[agent_name].setParent(None)
        del self._agent_settingdialogs_dict[agent_name]

    # Made this a seperate function because it will be easier to add your own function for different vehiclewithout making
    # a big mess
    def _get_update_from_other_modules(self, agent_name):
        #update ego_vehicle settings
        self.update_ego_vehicle_settings(agent_name)

    def update_ego_vehicle_settings(self, agent_name):
        if AgentTypes.EGO_VEHICLE.__str__() in agent_name:
            ego_vehicle_identifier = int(agent_name.replace('Ego Vehicle', ''))
            # Update hardware inputs according to current settings:
            self._agent_settingdialogs_dict[agent_name].combo_input.clear()
            self._agent_settingdialogs_dict[agent_name].combo_input.addItem('None')
            HardwareMPSettings = self.singleton_settings.get_settings(JOANModules.HARDWARE_MP)
            for keyboards in HardwareMPSettings.keyboards.values():
                self._agent_settingdialogs_dict[agent_name].combo_input.addItem(str(keyboards))
            for joysticks in HardwareMPSettings.joysticks.values():
                self._agent_settingdialogs_dict[agent_name].combo_input.addItem(str(joysticks))
            for sensodrives in HardwareMPSettings.sensodrives.values():
                self._agent_settingdialogs_dict[agent_name].combo_input.addItem(str(sensodrives))
            idx = self._agent_settingdialogs_dict[agent_name].combo_input.findText(
                self.module_settings.ego_vehicles[ego_vehicle_identifier].selected_input)
            if idx != -1:
                self._agent_settingdialogs_dict[agent_name].combo_input.setCurrentIndex(idx)

            # update available vehicles
            self._agent_settingdialogs_dict[agent_name].combo_car_type.clear()
            self._agent_settingdialogs_dict[agent_name].combo_car_type.addItem('None')
            self._agent_settingdialogs_dict[agent_name].combo_car_type.addItems(self.vehicle_tags)
            idx = self._agent_settingdialogs_dict[agent_name].combo_car_type.findText(self.module_settings.ego_vehicles[ego_vehicle_identifier].selected_car)
            if idx != -1:
                self._agent_settingdialogs_dict[agent_name].combo_car_type.setCurrentIndex(idx)

            # update available spawn_points:
            self._agent_settingdialogs_dict[agent_name].combo_spawnpoints.clear()
            self._agent_settingdialogs_dict[agent_name].combo_spawnpoints.addItem('None')
            self._agent_settingdialogs_dict[agent_name].combo_spawnpoints.addItems(self.spawn_points)
            idx = self._agent_settingdialogs_dict[agent_name].combo_spawnpoints.findText(
                self.module_settings.ego_vehicles[ego_vehicle_identifier].selected_spawnpoint)
            if idx != -1:
                self._agent_settingdialogs_dict[agent_name].combo_spawnpoints.setCurrentIndex(idx)
