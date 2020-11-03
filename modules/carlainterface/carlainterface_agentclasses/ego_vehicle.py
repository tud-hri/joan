from PyQt5 import uic, QtWidgets
import os
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
import random, os, sys, glob
import math
#TODO Maybe check this again, however it should not even start when it cant find the library the first time
import time
sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
import carla
from modules.joanmodules import JOANModules

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication

class EgoVehicleSettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings, module_manager, parent = None):
        super().__init__(parent)
        self.settings = settings
        self.module_manager = module_manager
        self.carla_interface_overall_settings = self.module_manager.module_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/ego_vehicle_settings_ui.ui"), self)
        self.msg_box = QMessageBox()
        self.msg_box.setTextFormat(QtCore.Qt.RichText)

        self.button_box_egovehicle_settings.button(self.button_box_egovehicle_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)
        self.btn_update.clicked.connect(self.update_ego_vehicle_settings)
        self.display_values()

        self.update_ego_vehicle_settings()
        self.show()

    def update_parameters(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_sw_controller.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        for settings in self.carla_interface_overall_settings.agents.values():
            if settings.identifier != self.settings.identifier: #exlude own settings
                if settings.selected_spawnpoint == self.combo_spawnpoints.currentText() and settings.selected_spawnpoint != 'None':
                    self.msg_box.setText('This spawnpoint was already chosen for another agent \n'
                                    'resetting spawnpoint to None')
                    self.msg_box.exec()
                    self.settings.selected_spawnpoint = 'None'
                    break
                else:
                    self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()

        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        self.display_values()

    def accept(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_sw_controller.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        for settings in self.carla_interface_overall_settings.agents.values():
            if settings.identifier != self.settings.identifier: #exlude own settings
                if settings.selected_spawnpoint == self.combo_spawnpoints.currentText() and settings.selected_spawnpoint != 'None':
                    self.msg_box.setText('This spawnpoint was already chosen for another agent \n'
                                     'resetting spawnpoint to None')
                    self.msg_box.exec()
                    self.settings.selected_spawnpoint = 'None'
                    break
            else:
                self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        super().accept()

    def display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.settings

        idx_controller = self.combo_sw_controller.findText(settings_to_display.selected_controller)
        self.combo_sw_controller.setCurrentIndex(idx_controller)

        idx_input = self.combo_input.findText(settings_to_display.selected_input)
        self.combo_input.setCurrentIndex(idx_input)

        idx_car = self.combo_car_type.findText(settings_to_display.selected_car)
        self.combo_car_type.setCurrentIndex(idx_car)

        self.combo_spawnpoints.setCurrentText(settings_to_display.selected_spawnpoint)

        self.spin_velocity.setValue(settings_to_display.velocity)
        self.check_box_set_vel.setChecked(settings_to_display.set_velocity)

    def _set_default_values(self):
        self.display_values(AgentTypes.EGO_VEHICLE.settings())
        
    def update_ego_vehicle_settings(self):
        # Update hardware inputs according to current settings:
        self.combo_input.clear()
        self.combo_input.addItem('None')
        HardwareManagerSettings = self.module_manager.singleton_settings.get_settings(JOANModules.HARDWARE_MP)
        for inputs in HardwareManagerSettings.inputs.values():
            self.combo_input.addItem(str(inputs))
        idx = self.combo_input.findText(
            self.settings.selected_input)
        if idx != -1:
            self.combo_input.setCurrentIndex(idx)

        # update available vehicles
        self.combo_car_type.clear()
        self.combo_car_type.addItem('None')
        self.combo_car_type.addItems(self.module_manager.vehicle_tags)
        idx = self.combo_car_type.findText(self.settings.selected_car)
        if idx != -1:
            self.combo_car_type.setCurrentIndex(idx)

        # update available spawn_points:
        self.combo_spawnpoints.clear()
        self.combo_spawnpoints.addItem('None')
        self.combo_spawnpoints.addItems(self.module_manager.spawn_points)
        idx = self.combo_spawnpoints.findText(
            self.settings.selected_spawnpoint)
        if idx != -1:
            self.combo_spawnpoints.setCurrentIndex(idx)

class EgoVehicleProcess:
    def __init__(self, carla_mp, settings, shared_variables):
        self.settings = settings
        self.shared_variables = shared_variables
        self.carlainterface_mp = carla_mp


        self._control = carla.VehicleControl()
        self._BP = random.choice(self.carlainterface_mp.vehicle_blueprint_library.filter("vehicle." + self.settings.selected_car))
        self._control = carla.VehicleControl()
        torque_curve = []
        gears = []

        torque_curve.append(carla.Vector2D(x=0, y=600))
        torque_curve.append(carla.Vector2D(x=14000, y=600))
        gears.append(carla.GearPhysicsControl(ratio=7.73, down_ratio=0.5, up_ratio=1))

        print(self.settings.selected_spawnpoint)

        if self.settings.selected_spawnpoint != 'None':
            self.spawned_vehicle = self.carlainterface_mp.world.spawn_actor(self._BP, self.carlainterface_mp.spawn_point_objects[
                self.carlainterface_mp.spawn_points.index(self.settings.selected_spawnpoint)])
            physics = self.spawned_vehicle.get_physics_control()
            physics.torque_curve = torque_curve
            physics.max_rpm = 14000
            physics.moi = 1.5
            physics.final_ratio = 1
            physics.clutch_strength = 1000  # very big no clutch
            physics.final_ratio = 1  # ratio from transmission to wheels
            physics.forward_gears = gears
            physics.mass = 2316
            physics.drag_coefficient = 0.24
            physics.gear_switch_time = 0
            self.spawned_vehicle.apply_physics_control(physics)


    def do(self):
        if self.settings.selected_input != 'None' and hasattr(self, 'spawned_vehicle'):
            self._control.steer = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].steering_angle /math.radians(450)
            self._control.reverse = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].reverse
            self._control.hand_brake = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].handbrake
            self._control.brake = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].brake
            self._control.throttle = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].throttle
            self.spawned_vehicle.apply_control(self._control)



    def destroy(self):
        if hasattr(self, 'spawned_vehicle'):
            self.spawned_vehicle.destroy()


class EgoVehicleSettings:
    """
    Class containing the default settings for an egovehicle
    """

    def __init__(self, identifier = ''):
        """
        Initializes the class with default variables
        """
        self.selected_input = 'None'
        self.selected_controller = 'None'
        self.selected_spawnpoint = 'Spawnpoint 0'
        self.selected_car = 'hapticslab.audi'
        self.velocity = 80
        self.set_velocity = False
        self.identifier = identifier

        self.agent_type = AgentTypes.EGO_VEHICLE.value

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)