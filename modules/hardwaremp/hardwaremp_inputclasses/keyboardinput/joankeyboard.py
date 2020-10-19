import os

import keyboard
from PyQt5 import QtWidgets, QtGui, uic

from modules.hardwaremp.hardwaremp_settings import KeyBoardSettings
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.hardwaremp.hardwaremp_inputclasses.baseinput import BaseInput


class KeyBoardSettingsDialog(QtWidgets.QDialog):
    """
      Class for the settings Dialog of a keyboardinput, this class should pop up whenever it is asked by the user or when
      creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
      """

    def __init__(self, keyboard_settings, parent=None):
        """
        Initializes the settings dialog with the appropriate keyboardinput settings
        :param keyboard_settings:
        :param parent:
        """
        super().__init__(parent)
        self.keyboard_settings = keyboard_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../uis/keyboard_settings_ui.ui"), self)

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
        Sets the settings as they are described in 'hardwarempSettings => KeyboardSettings)
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
    Main administrative class for Keyboard input (this is only to keep track of what is available in our main loop so this does not loop
    """

    def __init__(self, module_manager, hardware_input_list_key, settings):
        super().__init__(hardware_input_type=HardwareInputTypes.KEYBOARD, module_manager = module_manager)
        """
        Initializes the class
        :param hardware_manager_action:
        :param keyboard_tab:
        :param settings:
        """
        self.hardware_input_list_key = hardware_input_list_key
        self.settings = settings
        self.settings_dialog = None

        self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_dialog_from_button)
        self._hardware_input_tab.btn_visualization.setEnabled(False)

        self._open_settings_dialog()

    @property
    def get_hardware_input_list_key(self):
        return self.hardware_input_list_key

    def disable_remove_button(self):
        """
        Disables the remove_input_device keybaord button (useful for example when you dont want to be able to remove_input_device an input when the
        simulator is running)
                :return:
        """
        if self._hardware_input_tab.btn_remove_hardware.isEnabled() is True:
            self._hardware_input_tab.btn_remove_hardware.setEnabled(False)
        else:
            pass

    def enable_remove_button(self):
        """
        Enables the remove_input_device keyboardinput button
        :return:
        """
        if self._hardware_input_tab.btn_remove_hardware.isEnabled() is False:
            self._hardware_input_tab.btn_remove_hardware.setEnabled(True)
        else:
            pass

    def _open_settings_dialog_from_button(self):
        """
        Opens and shows the settings dialog from the button on the tab
        :return:
        """
        self._open_settings_dialog()
        if self.settings_dialog:
            self.settings_dialog.show()

    def _open_settings_dialog(self):
        """
        Sets the appropriate values for settings but does not actually show the dialog
        :return:
        """
        self.settings_dialog = KeyBoardSettingsDialog(self.settings)

