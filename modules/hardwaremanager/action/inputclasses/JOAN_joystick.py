import os
import hid
from PyQt5 import uic
from modules.hardwaremanager.action.settings import JoyStickSettings
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.joanmodules import JOANModules


# Arbitratry Joystick
class JOAN_Joystick(BaseInput):
    def __init__(self, hardware_manager_action, joystick_tab, settings: JoyStickSettings):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Joystick'
        self._joystick_tab = joystick_tab
        self._joystick_open = False
        self._joystick_tab.btn_remove_hardware.clicked.connect(self.remove_func)
        self._joystick = hid.device()

        self.settings = settings

        # Initialize Variables
        self.brake = 0
        self.steer = 0
        self.throttle = 0
        self.handbrake = False
        self.reverse = False

        # Load the appropriate settings tab and show it:
        self._settings_tab = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/joystick_settings_ui.ui"))
        self._settings_tab.show()

        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.Save).clicked.connect(self.settings_save_new_values)
        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.RestoreDefaults).clicked.connect(self.settings_set_default_values)
        self._joystick_tab.btn_settings.clicked.connect(self._settings_tab.show)

        for available_device in hid.enumerate():
            self._settings_tab.combo_available_devices.addItem(available_device['product_string'], userData=available_device)

    def open_connection_to_device(self):
        try:
            self._joystick.open(self.settings.device_vendor_id, self.settings.device_product_id)
            self._joystick_open = True
        except OSError:
            print('Connection to USB Joystick failed')  # TODO: move to messagebox
            self._joystick_open = False

    def settings_save_new_values(self):
        self.settings.min_steer = int(self._settings_tab.line_edit_min_steer.text())
        self.settings.max_steer = int(self._settings_tab.line_edit_max_steer.text())

        selected_device = self._settings_tab.combo_available_devices.currentData()
        if selected_device:
            self.settings.device_vendor_id = selected_device['vendor_id']
            self.settings.device_product_id = selected_device['product_id']
        else:
            self.settings.device_vendor_id = 0
            self.settings.device_product_id = 0

        self.open_connection_to_device()

    def settings_set_default_values(self):
        self.settings = JoyStickSettings()

        # Input defaults:
        self.brake = 0
        self.steer = 0
        self.throttle = 0
        self.handbrake = False
        self.reverse = False

        self._settings_tab.line_edit_min_steer.setText(str(self.settings.min_steer))
        self._settings_tab.line_edit_max_steer.setText(str(self.settings.max_steer))

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

            self.steer = round((((joystick_data[0]) + (joystick_data[1]) * 256) / (256 * 256)) * (self.settings.max_steer - self.settings.min_steer) - self.settings.max_steer)

        self._data['BrakeInput'] = self.brake
        self._data['ThrottleInput'] = self.throttle
        self._data['SteeringInput'] = self.steer
        self._data['Handbrake'] = self.handbrake
        self._data['Reverse'] = self.reverse

        return self._data
