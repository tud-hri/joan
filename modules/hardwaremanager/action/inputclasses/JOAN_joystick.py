import os
import hid
from PyQt5 import uic
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.joanmodules import JOANModules


# Arbitratry Joystick
class JOAN_Joystick(BaseInput):
    def __init__(self, hardware_manager_action, joystick_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Joystick'
        self._joystick_tab = joystick_tab
        self._joystick_open = False
        self._joystick_tab.btn_remove_hardware.clicked.connect(self.remove_func)
        self._joystick = hid.device()

        # Initialize Variables
        self._min_steer = 0
        self._max_steer = 0
        self.brake = 0
        self.steer = 0
        self.throttle = 0
        self.handbrake = False
        self.reverse = False

        # Load the appropriate settings tab and show it:
        self._settings_tab = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/joystick_settings_ui.ui"))
        self._settings_tab.show()

        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.Save).clicked.connect(self.settings_set_newvalues)
        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.RestoreDefaults).clicked.connect(self.settings_set_default_values)
        self._joystick_tab.btn_settings.clicked.connect(self._settings_tab.show)

        self._available_devices = []

        self.settings_set_default_values()

        for self._devices in hid.enumerate():
            self._settings_tab.combo_available_devices.addItem(self._devices['product_string'])
            self._available_devices.append(self._devices)

        self._settings_tab.combo_available_devices.currentTextChanged.connect(self.selected_input)

    def selected_input(self):
        for device in self._available_devices:
            if device['product_string'] == self._settings_tab.combo_available_devices.currentText():
                chosen_device = device

        try:
            self._joystick.open(chosen_device['vendor_id'], chosen_device['product_id'])
            self._joystick_open = True
        except:
            self._joystick_open = False

    def settings_set_newvalues(self):
        self._min_steer = int(self._settings_tab.line_edit_min_steer.text())
        self._max_steer = int(self._settings_tab.line_edit_max_steer.text())

    def settings_set_default_values(self):
        # Steering Range
        self._min_steer = -90
        self._max_steer = 90

        # Input defaults:
        self.brake = 0
        self.steer = 0
        self.throttle = 0
        self.handbrake = False
        self.reverse = False

        self._settings_tab.line_edit_min_steer.setText(str(self._min_steer))
        self._settings_tab.line_edit_max_steer.setText(str(self._max_steer))

    def remove_func(self):
        self.remove_tab(self._joystick_tab)

    def process(self):
        joystickdata = []
        if (self._carla_interface_data['vehicles'] is not None and self._joystick_open):
            self._carla_interface_data = self._action.read_news(JOANModules.CARLA_INTERFACE)

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._joystick_tab.groupBox.title():
                    self._joystick_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._joystick_tab.btn_remove_hardware.setEnabled(True)

            joystickdata = self._joystick.read(12, 1)

        if joystickdata != []:
            print(joystickdata)
            self.throttle = 100 - round((((joystickdata[9]) / 128)) * 100)
            if (self.throttle > 0):
                self.throttle = self.throttle
                self.brake = 0
            elif (self.throttle < 0):
                temp = self.throttle
                self.throttle = 0
                self.brake = -temp

            if joystickdata[10] == 2:
                self.handbrake = True
            elif joystickdata[10] == 8:
                self.reverse = True
            else:
                self.handbrake = False
                self.reverse = False

            self.steer = round((((joystickdata[0]) + (joystickdata[1]) * 256) / (256 * 256)) * (self._max_steer - self._min_steer) - self._max_steer)

        self._data['BrakeInput'] = self.brake
        self._data['ThrottleInput'] = self.throttle
        self._data['SteeringInput'] = self.steer
        self._data['Handbrake'] = self.handbrake
        self._data['Reverse'] = self.reverse

        return self._data
