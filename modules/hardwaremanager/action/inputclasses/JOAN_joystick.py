import os

import hid
from PyQt5 import uic, QtWidgets

from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.settings import JoyStickSettings
from modules.joanmodules import JOANModules


class JoystickSettingsDialog(QtWidgets.QDialog):
    def __init__(self, joystick_settings, parent=None):
        super().__init__(parent)
        self.joystick_settings = joystick_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/joystick_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(self._set_default_values)

        for available_device in hid.enumerate():
            self.combo_available_devices.addItem(available_device['product_string'], userData=available_device)

        self._display_values()
        self.show()

    def accept(self):
        self.joystick_settings.min_steer = self.spin_box_min_steer.value()
        self.joystick_settings.max_steer = self.spin_box_max_steer.value()

        selected_device = self.combo_available_devices.currentData()
        if selected_device:
            self.joystick_settings.device_vendor_id = selected_device['vendor_id']
            self.joystick_settings.device_product_id = selected_device['product_id']
        else:
            self.joystick_settings.device_vendor_id = 0
            self.joystick_settings.device_product_id = 0

        super().accept()

    def _display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.joystick_settings

        self.spin_box_min_steer.setValue(settings_to_display.min_steer)
        self.spin_box_max_steer.setValue(settings_to_display.max_steer)

        for index in range(self.combo_available_devices.count()):
            current_device = self.combo_available_devices.itemData(index)
            if current_device and settings_to_display.device_vendor_id == current_device['vendor_id'] and \
                    settings_to_display.device_product_id == current_device['product_id']:
                self.combo_available_devices.setCurrentIndex(index)
                break
            else:
                self.combo_available_devices.setCurrentIndex(0)

    def _set_default_values(self):
        self._display_values(JoyStickSettings())


class JOAN_Joystick(BaseInput):
    def __init__(self, hardware_manager_action, joystick_tab, settings: JoyStickSettings):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Joystick'
        self._joystick_tab = joystick_tab
        self.settings = settings

        # Initialize Variables
        self.brake = 0
        self.steer = 0
        self.throttle = 0
        self.handbrake = False
        self.reverse = False

        self.settings_dialog = None
        self._joystick_open = False
        self._joystick = hid.device()

        #  hook up buttons
        self._joystick_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._joystick_tab.btn_visualization.setEnabled(False)
        self._joystick_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def _open_settings_dialog(self):
        self.settings_dialog = JoystickSettingsDialog(self.settings)
        self.settings_dialog.accepted.connect(self._open_connection_to_device)

    def _open_connection_to_device(self):
        try:
            self._joystick.open(self.settings.device_vendor_id, self.settings.device_product_id)
            self._joystick_open = True
        except OSError:
            print('Connection to USB Joystick failed')  # TODO: move to messagebox
            self._joystick_open = False

    def remove_func(self):
        self.remove_tab(self._joystick_tab)

    def process(self):
        joystick_data = []
        if self._carla_interface_data['vehicles'] is not None and self._joystick_open:
            self._carla_interface_data = self._action.read_news(JOANModules.CARLA_INTERFACE)

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._joystick_tab.groupBox.title():
                    self._joystick_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._joystick_tab.btn_remove_hardware.setEnabled(True)

            joystick_data = self._joystick.read(12, 1)

        if joystick_data:
            print(joystick_data)
            self.throttle = 100 - round(((joystick_data[9]) / 128) * 100)
            if self.throttle > 0:
                self.throttle = self.throttle
                self.brake = 0
            elif self.throttle < 0:
                temp = self.throttle
                self.throttle = 0
                self.brake = -temp

            if joystick_data[10] == 2:
                self.handbrake = True
            elif joystick_data[10] == 8:
                self.reverse = True
            else:
                self.handbrake = False
                self.reverse = False

            self.steer = round(
                (((joystick_data[0]) + (joystick_data[1]) * 256) / (256 * 256)) * (self.settings.max_steer - self.settings.min_steer) - self.settings.max_steer)

        self._data['BrakeInput'] = self.brake
        self._data['ThrottleInput'] = self.throttle
        self._data['SteeringInput'] = self.steer
        self._data['Handbrake'] = self.handbrake
        self._data['Reverse'] = self.reverse

        return self._data
