import os
import keyboard
from PyQt5 import QtCore, uic
from modules.joanmodules import JOANModules
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.settings import KeyBoardSettings


class JOAN_Keyboard(BaseInput):
    def __init__(self, hardware_manager_action, keyboard_tab, settings: KeyBoardSettings):
        super().__init__(hardware_manager_action)
        self._keyboard_tab = keyboard_tab
        self.hardware_manager_action = hardware_manager_action
        self.settings = settings

        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False

        # Load the appropriate settings window and show it:
        self._settings_tab = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/keyboard_settings_ui.ui"))
        self._settings_tab.show()

        # Connect the settings button to the settings window
        self._keyboard_tab.btn_settings.clicked.connect(self._settings_tab.show)

        # Connect the hardware remove button to removing routine
        self._keyboard_tab.btn_remove_hardware.clicked.connect(self.remove_func)

        # Connect buttons of settings menu to methods:
        self._settings_tab.btn_set_keys.clicked.connect(self.settings_set_keys)
        # self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.RestoreDefaults).clicked.connect(self.settings_set_default_values)  TODO Fix
        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.Save).clicked.connect(self.settings_set_newvalues)
        self._settings_tab.keyPressEvent = self.settings_key_press_event
        self._settings_tab.slider_steer_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._settings_tab.slider_throttle_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._settings_tab.slider_brake_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._set_key_counter = 0

        # set the default settings when constructing:
        self.settings_tab_set_values()

        keyboard.hook(self.key_event, False)

    def remove_func(self):
        self.remove_tab(self._keyboard_tab)

    def settings_tab_set_values(self):
        # Key Names
        self._settings_tab.label_steer_left.setText(self.settings.steer_left_key)
        self._settings_tab.label_steer_right.setText(self.settings.steer_right_key)
        self._settings_tab.label_throttle.setText(self.settings.throttle_key)
        self._settings_tab.label_brake.setText(self.settings.brake_key)
        self._settings_tab.label_reverse.setText(self.settings.reverse_key)
        self._settings_tab.label_handbrake.setText(self.settings.handbrake_key)

        self._settings_tab.line_edit_min_steer.setText(str(self.settings.min_steer))
        self._settings_tab.line_edit_max_steer.setText(str(self.settings.max_steer))

        self._settings_tab.checkbox_autocenter.setChecked(self.settings.auto_center)

        self._settings_tab.slider_steer_sensitivity.setValue(self.settings.steer_sensitivity)
        self._settings_tab.slider_throttle_sensitivity.setValue(self.settings.throttle_sensitivity)
        self._settings_tab.slider_brake_sensitivity.setValue(self.settings.brake_sensitivity)

    def settings_update_sliders(self):
        self._settings_tab.label_steer_sensitivity.setText(str(self._settings_tab.slider_steer_sensitivity.value()))
        self._settings_tab.label_throttle_sensitivity.setText(str(self._settings_tab.slider_throttle_sensitivity.value()))
        self._settings_tab.label_brake_sensitivity.setText(str(self._settings_tab.slider_brake_sensitivity.value()))

    def settings_set_newvalues(self):
        self.settings.min_steer = int(self._settings_tab.line_edit_min_steer.text())
        self.settings.max_steer = int(self._settings_tab.line_edit_max_steer.text())
        self.settings.auto_center = self._settings_tab.checkbox_autocenter.isChecked()
        self.settings.steer_sensitivity = self._settings_tab.slider_steer_sensitivity.value()
        self.settings.brake_sensitivity = self._settings_tab.slider_brake_sensitivity.value()
        self.settings.throttle_sensitivity = self._settings_tab.slider_throttle_sensitivity.value()

    def settings_set_keys(self):
        self._settings_tab.btn_set_keys.setStyleSheet("background-color: lightgreen")
        self._settings_tab.btn_set_keys.clearFocus()
        self._settings_tab.button_box_settings.setEnabled(False)
        self._settings_tab.btn_set_keys.setEnabled(False)
        self._set_key_counter = 0
        self._settings_tab.label_steer_left.setStyleSheet("background-color: lightgreen")

    def settings_key_press_event(self, event):
        text = ""
        if self._settings_tab.btn_set_keys.isChecked():
            self._set_key_counter += 1

            if event.key() == QtCore.Qt.Key_Space:
                text = 'Spacebar'
            elif event.key() == QtCore.Qt.Key_Left:
                text = u"\u2190"
            elif event.key() == QtCore.Qt.Key_Right:
                text = u"\u2192"
            elif event.key() == QtCore.Qt.Key_Up:
                text = u"\u2191"
            elif event.key() == QtCore.Qt.Key_Down:
                text = u"\u2193"
            else:
                text = event.text().capitalize()

            if self._set_key_counter == 1:
                self._settings_tab.label_steer_left.setText(text)
                self._settings_tab.label_steer_left.setStyleSheet("background-color: none")
                self._settings_tab.label_steer_right.setStyleSheet("background-color: lightgreen")
                self.settings.steer_left_key = event.text()
            elif self._set_key_counter == 2:
                self._settings_tab.label_steer_right.setText(text)
                self._settings_tab.label_steer_right.setStyleSheet("background-color: none")
                self._settings_tab.label_throttle.setStyleSheet("background-color: lightgreen")
                self.settings.steer_right_key = event.text()
            elif self._set_key_counter == 3:
                self._settings_tab.label_throttle.setText(text)
                self._settings_tab.label_throttle.setStyleSheet("background-color: none")
                self._settings_tab.label_brake.setStyleSheet("background-color: lightgreen")
                self.settings.throttle_key = event.text()
            elif self._set_key_counter == 4:
                self._settings_tab.label_brake.setText(text)
                self._settings_tab.label_brake.setStyleSheet("background-color: none")
                self._settings_tab.label_reverse.setStyleSheet("background-color: lightgreen")
                self.settings.brake_key = event.text()
            elif self._set_key_counter == 5:
                self._settings_tab.label_reverse.setText(text)
                self._settings_tab.label_reverse.setStyleSheet("background-color: none")
                self._settings_tab.label_handbrake.setStyleSheet("background-color: lightgreen")
                self.settings.reverse_key = event.text()
            elif self._set_key_counter == 6:
                self._settings_tab.label_handbrake.setText(text)
                self._settings_tab.label_handbrake.setStyleSheet("background-color: none")
                self.settings.handbrake_key = event.text()
                self._settings_tab.btn_set_keys.setChecked(False)
                self._settings_tab.btn_set_keys.setStyleSheet("background-color: none")
                self._set_key_counter = 0
                self._settings_tab.button_box_settings.setEnabled(True)
                self._settings_tab.btn_set_keys.setEnabled(True)

    def key_event(self, key):
        if (key.event_type == keyboard.KEY_DOWN):
            if key.name == self.settings.throttle_key:
                self._throttle = True
            elif key.name == self.settings.brake_key:
                self._brake = True
            elif key.name == self.settings.steer_left_key:
                self._steer_left = True
                self._steer_right = False
            elif key.name == self.settings.steer_right_key:
                self._steer_right = True
                self._steer_left = False
            elif key.name == self.settings.handbrake_key:
                self._handbrake = True

        if (key.event_type == keyboard.KEY_UP):
            if key.name == self.settings.throttle_key:
                self._throttle = False
            elif key.name == self.settings.brake_key:
                self._brake = False
            elif key.name == self.settings.steer_left_key:
                self._steer_left = False
                self._steer_right = False
            elif key.name == self.settings.steer_right_key:
                self._steer_right = False
                self._steer_left = False
            elif key.name == self.settings.handbrake_key:
                self._handbrake = False
            elif key.name == self.settings.reverse_key:
                self._reverse = not self._reverse

    def process(self):
        # # If there are cars in the simulation add them to the controllable car combobox
        if (self._carla_interface_data['vehicles'] is not None):
            self._carla_interface_data = self._action.read_news(JOANModules.CARLA_INTERFACE)

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._keyboard_tab.groupBox.title():
                    self._keyboard_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._keyboard_tab.btn_remove_hardware.setEnabled(True)

        # Throttle:
        if self._throttle and self._data['ThrottleInput'] < 100:
            self._data['ThrottleInput'] = self._data['ThrottleInput'] + (5 * self.settings.throttle_sensitivity / 100)
        elif self._data['ThrottleInput'] > 0 and not self._throttle:
            self._data['ThrottleInput'] = self._data['ThrottleInput'] - (5 * self.settings.throttle_sensitivity / 100)

        # Brake:
        if self._brake and self._data['BrakeInput'] < 100:
            self._data['BrakeInput'] = self._data['BrakeInput'] + (5 * self.settings.brake_sensitivity / 100)
        elif self._data['BrakeInput'] > 0 and not self._brake:
            self._data['BrakeInput'] = self._data['BrakeInput'] - (5 * self.settings.brake_sensitivity / 100)

        # Steering:
        if self._steer_left and self.settings.max_steer > self._data['SteeringInput'] > self.settings.min_steer:
            self._data['SteeringInput'] = self._data['SteeringInput'] - (4 * self.settings.steer_sensitivity / 100)
        elif self._steer_right and self.settings.min_steer < self._data['SteeringInput'] < self.settings.max_steer:
            self._data['SteeringInput'] = self._data['SteeringInput'] + (4 * self.settings.steer_sensitivity / 100)
        elif self._data['SteeringInput'] > 0 and self.settings.auto_center:
            self._data['SteeringInput'] = self._data['SteeringInput'] - (2 * self.settings.steer_sensitivity / 100)
        elif self._data['SteeringInput'] < 0 and self.settings.auto_center:
            self._data['SteeringInput'] = self._data['SteeringInput'] + (2 * self.settings.steer_sensitivity / 100)

        # Reverse
        self._data['Reverse'] = self._reverse

        # Handbrake
        self._data['Handbrake'] = self._handbrake

        return self._data
