from .basevehicle import Basevehicle
from modules.carlainterface.action.carlainterfacesettings import EgoVehicleSettings
from modules.joanmodules import JOANModules

from PyQt5 import uic, QtWidgets
import os, math

class EgovehicleSettingsDialog(QtWidgets.QDialog):
    def __init__(self, egovehicle_settings, parent=None):
        super().__init__(parent)
        self.egovehicle_settings = egovehicle_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/vehicle_settings_ui.ui"), self)

        self.button_box_egovehicle_settings.button(self.button_box_egovehicle_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)
        self._display_values()

    def update_parameters(self):
        self.egovehicle_settings._velocity = self.spin_velocity.value()
        self.egovehicle_settings._selected_input = self.combo_input.currentText()
        self.egovehicle_settings._selected_controller = self.combo_sw_controller.currentText()
        self.egovehicle_settings._selected_car = self.combo_car_type.currentText()
        self.egovehicle_settings._selected_spawnpoint = self.spin_spawn_points.value()
        self.egovehicle_settings._set_velocity= self.check_box_set_vel.isChecked()
        self._display_values()

    def accept(self):
        self.egovehicle_settings._velocity = self.spin_velocity.value()
        self.egovehicle_settings._selected_input = self.combo_input.currentText()
        self.egovehicle_settings._selected_controller = self.combo_sw_controller.currentText()
        self.egovehicle_settings._selected_car = self.combo_car_type.currentText()
        self.egovehicle_settings._selected_spawnpoint = self.spin_spawn_points.value()
        self.egovehicle_settings._set_velocity= self.check_box_set_vel.isChecked()

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

        self.spin_velocity.setValue(settings_to_display._velocity)
        self.check_box_set_vel.setChecked(settings_to_display._set_velocity)


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
        self._vehicle_tab.btn_settings.clicked.connect(self._open_settings_dialog_from_button)

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
        return self.settings._selected_input

    @property
    def selected_sw_controller(self):
        return self.settings._selected_controller

    @property
    def vehicle_nr(self):
        return self._vehicle_nr

    def _open_settings_dialog(self):
        self.get_available_controllers()
        self.get_available_inputs()
        self.settings_dialog._display_values()

    def _open_settings_dialog_from_button(self):
        self.get_available_controllers()
        self.get_available_inputs()
        self.settings_dialog._display_values()
        self.settings_dialog.show()


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
        car = self.spawned_vehicle

        if self.settings._selected_input != 'None':
            self._control.steer = data[self.settings._selected_input]['SteeringInput'] / 450
            self._control.reverse = data[self.settings._selected_input]['Reverse']
            self._control.hand_brake = data[self.settings._selected_input]['Handbrake']
            self._control.brake = data[self.settings._selected_input]['BrakeInput'] / 100

            if self.settings._set_velocity:
                vel_error = self.settings._velocity - (math.sqrt(
                    car.get_velocity().x ** 2 + car.get_velocity().y ** 2 + car.get_velocity().z ** 2) * 3.6)
                vel_error_rate = (math.sqrt(
                    car.get_acceleration().x ** 2 + car.get_acceleration().y ** 2 + car.get_acceleration().z ** 2) * 3.6)
                error_velocity = [vel_error, vel_error_rate]

                pd_vel_output = self.egovehicle_velocityPD(error_velocity)
                if pd_vel_output < 0:
                    self._control.brake = -pd_vel_output
                    self._control.throttle = 0
                    if pd_vel_output < -1:
                        self._control.brake = 1
                elif pd_vel_output > 0:
                    if self._control.brake == 0:
                        self._control.throttle = pd_vel_output
                    else:
                        self._control.throttle = 0



            else:
                self._control.throttle = data[self.settings._selected_input]['ThrottleInput'] / 100


            self.spawned_vehicle.apply_control(self._control)

    def egovehicle_velocityPD(self, error):
        _kp_vel = 50
        _kd_vel = 1
        temp = _kp_vel * error[0] + _kd_vel * error[1]

        if temp > 100:
            temp = 100

        output = temp/100

        return output

    def remove_ego_agent(self):
        self._vehicle_tab.setParent(None)
        self.destroy_car()

        self.module_action.settings.ego_vehicles.remove(self.settings)
        self.module_action.vehicles.remove(self)
