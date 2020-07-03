from .basevehicle import Basevehicle
from modules.agentmanager.action.agentmanagersettings import EgoVehicleSettings
from modules.joanmodules import JOANModules

from PyQt5 import uic, QtWidgets
import os

class EgovehicleSettingsDialog(QtWidgets.QDialog):
    def __init__(self, egovehicle_settings, parent=None):
        super().__init__(parent)
        self.egovehicle_settings = egovehicle_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/vehicle_settings_ui.ui"), self)

        self.button_box_egovehicle_settings.button(self.button_box_egovehicle_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self._display_values()



    def accept(self):
        self.egovehicle_settings._selected_input = self.combo_input.currentText()
        self.egovehicle_settings._selected_controller = self.combo_sw_controller.currentText()
        self.egovehicle_settings._selected_car = self.combo_car_type.currentText()
        self.egovehicle_settings._selected_spawnpoint = self.spin_spawn_points.value()

        super().accept()

    def _display_values(self, settings_to_display = None):
        if not settings_to_display:
            settings_to_display = self.egovehicle_settings

        idx_controller = self.combo_sw_controller.findText(settings_to_display._selected_controller)
        self.combo_sw_controller.setCurrentIndex(idx_controller)

        idx_input = self.combo_input.findText(settings_to_display._selected_input)
        self.combo_input.setCurrentIndex(idx_input)

        idx_car = self.combo_car_type.findText(settings_to_display._selected_car)
        self.combo_car_type.setCurrentIndex(idx_car)

        self.spin_spawn_points.setValue(settings_to_display._selected_spawnpoint)


    def _set_default_values(self):
        self._display_values(EgoVehicleSettings())

class Egovehicle(Basevehicle):
    def __init__(self, agent_manager_action, car_nr, nr_spawn_points, tags, settings: EgoVehicleSettings):
        super().__init__(agent_manager_action)

        self.settings = settings

        self._vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/vehicletab.ui"))
        self._vehicle_tab.group_car.setTitle('Car ' + str(car_nr+1))
        self._spawned = False
        self._hardware_data = {}
        self._sw_controller_data = {}
        self._vehicle_nr = 'Car ' + str(car_nr+1)

        self._vehicle_tab.btn_destroy.setEnabled(False)

        self._vehicle_tab.btn_spawn.clicked.connect(self.spawn_car)
        self._vehicle_tab.btn_destroy.clicked.connect(self.destroy_car)
        self._vehicle_tab.btn_remove_ego_agent.clicked.connect(self.remove_ego_agent)
        self._vehicle_tab.btn_settings.clicked.connect(self._open_settings_dialog)

        self.settings_dialog = EgovehicleSettingsDialog(self.settings)

        for item in tags:
            self.settings_dialog.combo_car_type.addItem(item)


        self.settings_dialog.spin_spawn_points.setRange(0, nr_spawn_points - 1)


        self._open_settings_dialog()



    @property
    def vehicle_tab(self):
        return self._vehicle_tab

    @property
    def selected_input(self):
        return self._selected_input

    @property
    def selected_sw_controller(self):
        return self._sw_controller

    @property
    def vehicle_nr(self):
        return self._vehicle_nr

    def _open_settings_dialog(self):
        self.get_available_controllers()
        self.get_available_inputs()
        self.settings_dialog._display_values()
        self.settings_dialog.show()
        pass

    def update_sw_controller(self):
        self._sw_controller = self._vehicle_tab.combo_sw_controller.currentText()

    def update_input(self):
        self._selected_input = self._vehicle_tab.combo_input.currentText()

    def get_available_inputs(self):
        self.settings_dialog.combo_input.clear()
        self.settings_dialog.combo_input.addItem('None')
        self._hardware_data = self.module_action.read_news(JOANModules.HARDWARE_MANAGER)
        for keys in self._hardware_data:
            self.settings_dialog.combo_input.addItem(str(keys))

    def get_available_controllers(self):
        self.settings_dialog.combo_sw_controller.clear()
        self.settings_dialog.combo_sw_controller.addItem('None')
        self._sw_controller_data = self.module_action.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        for keys in self._sw_controller_data:
            self.settings_dialog.combo_sw_controller.addItem(str(keys))


    def destroy_inputs(self):
        self._vehicle_tab.combo_input.clear()
        self._vehicle_tab.combo_input.addItem('None')


    def apply_control(self, data):
        if self._selected_input != 'None':
            self._control.steer = data[self._selected_input]['SteeringInput'] / 450
            self._control.throttle = data[self._selected_input]['ThrottleInput'] / 100
            self._control.brake = data[self._selected_input]['BrakeInput'] / 100
            self._control.reverse = data[self._selected_input]['Reverse']
            self._control.hand_brake = data[self._selected_input]['Handbrake']
            self.spawned_vehicle.apply_control(self._control)

    def remove_ego_agent(self):
        self._vehicle_tab.setParent(None)
        self.destroy_car()

        self.module_action.vehicles.remove(self)
