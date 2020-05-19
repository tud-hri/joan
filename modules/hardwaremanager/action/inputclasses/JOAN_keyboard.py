import os

import keyboard
from PyQt5 import QtWidgets, QtGui, uic

from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.settings import KeyBoardSettings
from modules.joanmodules import JOANModules


class KeyBoardSettingsDialog(QtWidgets.QDialog):
    def __init__(self, keyboard_settings, parent=None):
        super().__init__(parent)
        self.keyboard_settings = keyboard_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/keyboard_settings_ui.ui"), self)

        self.slider_steer_sensitivity.valueChanged.connect(lambda new_value: self.label_steer_sensitivity.setText(str(new_value)))
        self.slider_throttle_sensitivity.valueChanged.connect(lambda new_value: self.label_throttle_sensitivity.setText(str(new_value)))
        self.slider_brake_sensitivity.valueChanged.connect(lambda new_value: self.label_brake_sensitivity.setText(str(new_value)))

        self._set_key_counter = 0

        self.btn_set_keys.clicked.connect(self._start_key_setting_sequence)
        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(self._set_default_values)

        self.set_key_sequence_labels = [self.label_steer_left, self.label_steer_right, self.label_throttle, self.label_brake, self.label_reverse,
                                        self.label_handbrake]

        self._display_values()
        self.show()

    def accept(self):
        all_desired_keys = [self.label_steer_left.text(), self.label_steer_right.text(), self.label_throttle.text(), self.label_brake.text(),
                            self.label_reverse.text(), self.label_handbrake.text()]
        if len(all_desired_keys) != len(set(all_desired_keys)):
            answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                    'So are trying to set the same key for two command, this may lead to undesired behavior. Are you sure?',
                                                    buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Cancel:
                return

        self.keyboard_settings.min_steer = self.spin_box_min_steer.value()
        self.keyboard_settings.max_steer = self.spin_box_max_steer.value()
        self.keyboard_settings.auto_center = self.checkbox_autocenter.isChecked()
        self.keyboard_settings.steer_sensitivity = self.slider_steer_sensitivity.value()
        self.keyboard_settings.brake_sensitivity = self.slider_brake_sensitivity.value()
        self.keyboard_settings.throttle_sensitivity = self.slider_throttle_sensitivity.value()

        self.keyboard_settings.steer_left_key = QtGui.QKeySequence(self.label_steer_left.text())[0]
        self.keyboard_settings.steer_right_key = QtGui.QKeySequence(self.label_steer_right.text())[0]
        self.keyboard_settings.throttle_key = QtGui.QKeySequence(self.label_throttle.text())[0]
        self.keyboard_settings.brake_key = QtGui.QKeySequence(self.label_brake.text())[0]
        self.keyboard_settings.reverse_key = QtGui.QKeySequence(self.label_reverse.text())[0]
        self.keyboard_settings.handbrake_key = QtGui.QKeySequence(self.label_handbrake.text())[0]
        super().accept()

    def _display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.keyboard_settings

        self.label_steer_left.setText(QtGui.QKeySequence(settings_to_display.steer_left_key).toString())
        self.label_steer_right.setText(QtGui.QKeySequence(settings_to_display.steer_right_key).toString())
        self.label_throttle.setText(QtGui.QKeySequence(settings_to_display.throttle_key).toString())
        self.label_brake.setText(QtGui.QKeySequence(settings_to_display.brake_key).toString())
        self.label_reverse.setText(QtGui.QKeySequence(settings_to_display.reverse_key).toString())
        self.label_handbrake.setText(QtGui.QKeySequence(settings_to_display.handbrake_key).toString())

        self.spin_box_min_steer.setValue(settings_to_display.min_steer)
        self.spin_box_max_steer.setValue(settings_to_display.max_steer)

        self.checkbox_autocenter.setChecked(settings_to_display.auto_center)

        self.slider_steer_sensitivity.setValue(settings_to_display.steer_sensitivity)
        self.slider_throttle_sensitivity.setValue(settings_to_display.throttle_sensitivity)
        self.slider_brake_sensitivity.setValue(settings_to_display.brake_sensitivity)

    def _set_default_values(self):
        self._display_values(KeyBoardSettings())

    def _start_key_setting_sequence(self):
        self.btn_set_keys.setStyleSheet("background-color: lightgreen")
        self.btn_set_keys.clearFocus()
        self.button_box_settings.setEnabled(False)
        self.btn_set_keys.setEnabled(False)
        self._set_key_counter = 0
        self.set_key_sequence_labels[self._set_key_counter].setStyleSheet("background-color: lightgreen")

    def keyPressEvent(self, event):
        if self.btn_set_keys.isChecked():
            try:
                self.set_key_sequence_labels[self._set_key_counter].setText(QtGui.QKeySequence(event.key()).toString())
                self.set_key_sequence_labels[self._set_key_counter].setStyleSheet("background-color: none")
                self.set_key_sequence_labels[self._set_key_counter + 1].setStyleSheet("background-color: lightgreen")
                self._set_key_counter += 1
            except IndexError:  # reached the last key
                self.btn_set_keys.setChecked(False)
                self.btn_set_keys.setStyleSheet("background-color: none")
                self._set_key_counter = 0
                self.button_box_settings.setEnabled(True)
                self.btn_set_keys.setEnabled(True)


class JOAN_Keyboard(BaseInput):
    def __init__(self, hardware_manager_action, keyboard_tab, settings: KeyBoardSettings):
        super().__init__(hardware_manager_action)
        self._keyboard_tab = keyboard_tab
        self.hardware_manager_action = hardware_manager_action
        self.settings = settings
        self.settings_dialog = None

        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False

        # Connect the settings button to the settings window
        self._keyboard_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._keyboard_tab.btn_remove_hardware.clicked.connect(self.remove_func)
        self._keyboard_tab.btn_visualization.setEnabled(False)

        keyboard.hook(self.key_event, False)

        self._open_settings_dialog()

    def remove_func(self):
        self.remove_tab(self._keyboard_tab)

    def _open_settings_dialog(self):
        self.settings_dialog = KeyBoardSettingsDialog(self.settings)

    def key_event(self, key):
        if key.event_type == keyboard.KEY_DOWN:
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

        if key.event_type == keyboard.KEY_UP:
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
        if self._carla_interface_data['vehicles']:
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
