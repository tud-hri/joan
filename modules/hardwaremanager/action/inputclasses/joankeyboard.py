import os

import keyboard
from PyQt5 import QtWidgets, QtGui, uic

from modules.hardwaremanager.action.hardwaremanagersettings import KeyBoardSettings
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.joanmodules import JOANModules


class KeyBoardSettingsDialog(QtWidgets.QDialog):
    """
      Class for the settings Dialog of a keyboard, this class should pop up whenever it is asked by the user or when
      creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
      """
    def __init__(self, keyboard_settings, parent=None):
        """
        Initializes the settings dialog with the appropriate keyboard settings
        :param keyboard_settings:
        :param parent:
        """
        super().__init__(parent)
        self.keyboard_settings = keyboard_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/keyboard_settings_ui.ui"), self)

        self.slider_steer_sensitivity.valueChanged.connect(
            lambda new_value: self.label_steer_sensitivity.setText(str(new_value)))
        self.slider_throttle_sensitivity.valueChanged.connect(
            lambda new_value: self.label_throttle_sensitivity.setText(str(new_value)))
        self.slider_brake_sensitivity.valueChanged.connect(
            lambda new_value: self.label_brake_sensitivity.setText(str(new_value)))

        self._set_key_counter = 0

        self.btn_set_keys.clicked.connect(self._start_key_setting_sequence)
        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)

        self.set_key_sequence_labels = [self.label_steer_left, self.label_steer_right, self.label_throttle,
                                        self.label_brake, self.label_reverse,
                                        self.label_handbrake]

        self._display_values()
        # self.show()

    def accept(self):
        """
        Accepts the selected settings and saves them internally.
        NOTE: will return an error if trying to set 2 buttons for the same functionality
        :return:
        """
        all_desired_keys = [self.label_steer_left.text(), self.label_steer_right.text(), self.label_throttle.text(),
                            self.label_brake.text(),
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
        """
        Displays the settings that are currently being used (internally)
        :param settings_to_display:
        :return:
        """
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
        """
        Sets the settings as they are described in 'HardwaremanagerSettings => KeyboardSettings)
        :return:
        """
        self._display_values(KeyBoardSettings())

    def _start_key_setting_sequence(self):
        """
        Starts the sequence that will run through the different available inputs.
        :return:
        """
        self.btn_set_keys.setStyleSheet("background-color: lightgreen")
        self.btn_set_keys.clearFocus()
        self.button_box_settings.setEnabled(False)
        self.btn_set_keys.setEnabled(False)
        self._set_key_counter = 0
        self.set_key_sequence_labels[self._set_key_counter].setStyleSheet("background-color: lightgreen")

    def keyPressEvent(self, event):
        """
        Overwrites the built in 'keyPressEvent' function of PyQt with this function. Checks which key is pressed and handles
        it accordingly.
        :param event:
        :return:
        """
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


class JOANKeyboard(BaseInput):
    """
    Main class for the Keyboard input, inherits from BaseInput (as it should!)
    """

    def __init__(self, hardware_manager_action, keyboard_tab, settings: KeyBoardSettings):
        """
        Initializes the class
        :param hardware_manager_action:
        :param keyboard_tab:
        :param settings:
        """
        super().__init__(hardware_manager_action)
        self._keyboard_tab = keyboard_tab
        self.hardware_manager_action = hardware_manager_action
        self.settings = settings
        self.settings_dialog = None

        self.module_action = hardware_manager_action

        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False

        # Connect the settings button to the settings window
        self._keyboard_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._keyboard_tab.btn_settings.clicked.connect(self._open_settings_from_button)
        self._keyboard_tab.btn_remove_hardware.clicked.connect(self.remove_func)
        self._keyboard_tab.btn_visualization.setEnabled(False)

        keyboard.hook(self.key_event, False)
        self._open_settings_dialog()

    def initialize(self):
        """
        Function is called when initialize is pressed, can be altered for more functionality
        :return:
        """
        print('initializing keyboard')

    def disable_remove_button(self):
        """
        Disables the remove keybaord button (useful for example when you dont want to be able to remove an input when the
        simulator is running)
                :return:
        """
        if self._keyboard_tab.btn_remove_hardware.isEnabled() is True:
            self._keyboard_tab.btn_remove_hardware.setEnabled(False)
        else:
            pass

    def enable_remove_button(self):
        """
        Enables the remove keyboard button
        :return:
        """
        if self._keyboard_tab.btn_remove_hardware.isEnabled() is False:
            self._keyboard_tab.btn_remove_hardware.setEnabled(True)
        else:
            pass

    def remove_func(self):
        """
        Removes the keyboard from the widget and settings
        NOTE: calls 'self.remove_tab' which is a function of the BaseInput class, if you do not do this the tab will not
        actually disappear from the module.
        :return:
        """
        self.remove_tab(self._keyboard_tab)
        self.module_action.settings.key_boards.remove(self.settings)

    def _open_settings_from_button(self):
        """
        Opens and shows the settings dialog from the button on the tab
        :return:
        """
        if self.settings_dialog:
            self.settings_dialog.show()

    def _open_settings_dialog(self):
        """
        Sets the appropriate values for settings but does not actually show the dialog
        :return:
        """
        self.settings_dialog = KeyBoardSettingsDialog(self.settings)


    def key_event(self, key):
        """
        Distinguishes which key (that has been set before) is pressed and sets a boolean for the appropriate action.
        :param key:
        :return:
        """
        boolean_key_press_value = key.event_type == keyboard.KEY_DOWN
        int_key_identifier = QtGui.QKeySequence(key.name)[0]

        if int_key_identifier == self.settings.throttle_key:
            self._throttle = boolean_key_press_value
        elif int_key_identifier == self.settings.brake_key:
            self._brake = boolean_key_press_value
        elif int_key_identifier == self.settings.steer_left_key:
            self._steer_left = boolean_key_press_value
            if boolean_key_press_value:
                self._steer_right = False
        elif int_key_identifier == self.settings.steer_right_key:
            self._steer_right = boolean_key_press_value
            if boolean_key_press_value:
                self._steer_left = False
        elif int_key_identifier == self.settings.handbrake_key:
            self._handbrake = boolean_key_press_value
        elif int_key_identifier == self.settings.reverse_key and boolean_key_press_value:
            self._reverse = not self._reverse

    def process(self):
        """
        Processes all the inputs of the keyboard and writes them to self._data which is then written to the news in the
        action class
        :return: self._data a dictionary containing :
            self._data['BrakeInput'] = self.brake
            self._data['ThrottleInput'] = self.throttle
            self._data['SteeringInput'] = self.steer
            self._data['Handbrake'] = self.handbrake
            self._data['Reverse'] = self.reverse
        """
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
