import os

import hid
from PyQt5 import uic, QtWidgets, QtCore

from modules.hardwaremanager.action.hardwaremanagersettings import JoyStickSettings
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.hwinputtypes import HardwareInputTypes

class JoystickSettingsDialog(QtWidgets.QDialog):
    """
    Class for the settings Dialog of a joystick, this class should pop up whenever it is asked by the user or when
    creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
    """

    def __init__(self, joystick_settings, parent=None):
        """
        Initializes the joystick class with the proper settings.
        :param joystick_settings:
        :param parent:
        """
        super().__init__(parent)
        self.joystick_settings = joystick_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/joystick_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_settings)

        for available_device in hid.enumerate():
            self.combo_available_devices.addItem(available_device['product_string'], userData=available_device)

        self._joystick = hid.device()
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.preview_joystick_values)

        self.useSeparateBrakeChannelCheckBox.stateChanged.connect(self._update_brake_channel_enabled)
        self.useDoubleSteerResolutionCheckBox.stateChanged.connect(self._update_second_steer_channel_enabled)
        self.displayCurrentInputCheckBox.stateChanged.connect(self._enable_previewing_values)
        self.dofSpinBox.valueChanged.connect(self._update_degrees_of_freedom)
        self.combo_available_devices.currentIndexChanged.connect(self._enable_preview_checkbox)
        self.presetsComboBox.currentIndexChanged.connect(self._set_presets)

        self.presetsComboBox.addItem("Custom")
        self.presetsComboBox.addItem("XBOX")
        self.presetsComboBox.addItem("PlayStation")

        self.dofSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.gasChannelSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.useSeparateBrakeChannelCheckBox.stateChanged.connect(self._set_preset_combo_box_to_custom)
        self.brakeChannelSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.steerFirstChannelSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.useDoubleSteerResolutionCheckBox.stateChanged.connect(self._set_preset_combo_box_to_custom)
        self.steerSecondChannelSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.handBrakeChannelSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.handBrakeValueSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.reverseChannelSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)
        self.reverseValueSpinBox.valueChanged.connect(self._set_preset_combo_box_to_custom)

        self.value_preview_labels = []
        self.value_preview_check_boxes = []

        self._display_settings()
        # self.show()

    def preview_joystick_values(self):
        """
        This function shows the current values of a selected joystick before actually saving the settings. This is
        useful because now we can see which button would be which parameter.
        :return:
        """
        try:
            joystick_data = self._joystick.read(self.dofSpinBox.value())

            for index, value in enumerate(joystick_data):
                if self.value_preview_check_boxes[index].isChecked():
                    self.value_preview_labels[index].setText(str(value))
                else:
                    self.value_preview_labels[index].setText(" - ")

        except ValueError:
            pass  # joystick connection is not open

    def accept(self):
        """
        Accepts the selected settings and saves them internally.
        :return:
        """
        self.joystick_settings.min_steer = self.spin_box_min_steer.value()
        self.joystick_settings.max_steer = self.spin_box_max_steer.value()

        selected_device = self.combo_available_devices.currentData()
        if selected_device:
            self.joystick_settings.device_vendor_id = selected_device['vendor_id']
            self.joystick_settings.device_product_id = selected_device['product_id']
        else:
            self.joystick_settings.device_vendor_id = 0
            self.joystick_settings.device_product_id = 0

        self.joystick_settings.degrees_of_freedom = self.dofSpinBox.value()
        self.joystick_settings.gas_channel = self.gasChannelSpinBox.value()
        self.joystick_settings.use_separate_brake_channel = self.useSeparateBrakeChannelCheckBox.isChecked()
        self.joystick_settings.brake_channel = self.brakeChannelSpinBox.value()
        self.joystick_settings.first_steer_channel = self.steerFirstChannelSpinBox.value()
        self.joystick_settings.use_double_steering_resolution = self.useDoubleSteerResolutionCheckBox.isChecked()
        self.joystick_settings.second_steer_channel = self.steerSecondChannelSpinBox.value()
        self.joystick_settings.hand_brake_channel = self.handBrakeChannelSpinBox.value()
        self.joystick_settings.hand_brake_value = self.handBrakeValueSpinBox.value()
        self.joystick_settings.reverse_channel = self.reverseChannelSpinBox.value()
        self.joystick_settings.reverse_value = self.reverseValueSpinBox.value()

        super().accept()

    def _set_preset_combo_box_to_custom(self):
        """
        Sets the button mapping preset combobox to 'custom'
        :return:
        """
        self.presetsComboBox.setCurrentIndex(0)

    def _set_presets(self):
        """
        Sets the presets
        :return:
        """
        if self.presetsComboBox.currentText().lower() != 'custom':
            preset_settings = JoyStickSettings.get_preset_settings(self.presetsComboBox.currentText().lower())
            self._display_settings(settings_to_display=preset_settings, only_keymap=True)

    def _display_settings(self, settings_to_display=None, only_keymap=False):
        """
        Displays the settings that are currently being used (internally)
        :param settings_to_display:
        :param only_keymap:
        :return:
        """
        if not settings_to_display:
            settings_to_display = self.joystick_settings

        if not only_keymap:
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

        self.dofSpinBox.setValue(settings_to_display.degrees_of_freedom)
        self.gasChannelSpinBox.setValue(settings_to_display.gas_channel)
        self.useSeparateBrakeChannelCheckBox.setChecked(settings_to_display.use_separate_brake_channel)
        self.brakeChannelSpinBox.setValue(settings_to_display.brake_channel)
        self.steerFirstChannelSpinBox.setValue(settings_to_display.first_steer_channel)
        self.useDoubleSteerResolutionCheckBox.setChecked(settings_to_display.use_double_steering_resolution)
        self.steerSecondChannelSpinBox.setValue(settings_to_display.second_steer_channel)
        self.handBrakeChannelSpinBox.setValue(settings_to_display.hand_brake_channel)
        self.handBrakeValueSpinBox.setValue(settings_to_display.hand_brake_value)
        self.reverseChannelSpinBox.setValue(settings_to_display.reverse_channel)
        self.reverseValueSpinBox.setValue(settings_to_display.reverse_value)

    def _set_default_settings(self):
        """
        Sets the settings as they are described in 'HardwaremanagerSettings => JoystickSettings)
        :return:
        """
        self._display_settings(JoyStickSettings())

    def _update_brake_channel_enabled(self, value):
        """
        Updates the controller channel that will be used for braking
        :param value:
        :return:
        """
        self.brakeChannelSpinBox.setEnabled(value)

    def _update_second_steer_channel_enabled(self, value):
        """
        If the resolution of the joystick is high it might use 2 channels for steering, this function enables that
        functionality
        :param value:
        :return:
        """
        self.steerSecondChannelSpinBox.setEnabled(value)

    def _enable_preview_checkbox(self):
        """
        Toggles the preview checkbox availability depending on whether there is a device
        :return:
        """
        if self.combo_available_devices.currentData():
            self.displayCurrentInputCheckBox.setEnabled(True)
        else:
            self.displayCurrentInputCheckBox.setChecked(False)
            self.displayCurrentInputCheckBox.setEnabled(False)

    def _enable_previewing_values(self, value):
        """
        Toggles the preview checkbox availability depending on whether there is a value
        :param value:
        :return:
        """
        if value:
            selected_device = self.combo_available_devices.currentData()
            self._joystick.open(selected_device['vendor_id'], selected_device['product_id'])
            self.update_timer.start()
        else:
            self.update_timer.stop()
            self._joystick.close()

        for widget in self.value_preview_labels:
            widget.setEnabled(value)

        for widget in self.value_preview_check_boxes:
            widget.setEnabled(value)

    def _update_degrees_of_freedom(self, value):
        """
        Updates the degrees of freedom according to how many inputs the joystick has available.
        :param value:
        :return:
        """
        self.displayCurrentInputCheckBox.setChecked(False)

        for index in reversed(range(self.currentInputGroupBox.layout().count())):
            widget = self.currentInputGroupBox.layout().itemAt(index).widget()
            widget.setParent(None)
            widget.deleteLater()

        self.value_preview_labels = []
        self.value_preview_check_boxes = []

        for index in range(value):
            check_box = QtWidgets.QCheckBox()
            check_box.setEnabled(self.displayCurrentInputCheckBox.isChecked())
            check_box.setChecked(True)

            display_label = QtWidgets.QLabel(" - ")
            display_label.setEnabled(self.displayCurrentInputCheckBox.isChecked())

            self.currentInputGroupBox.layout().addWidget(check_box, index, 0)
            self.currentInputGroupBox.layout().addWidget(QtWidgets.QLabel("value #" + str(index)), index, 1)
            self.currentInputGroupBox.layout().addWidget(display_label, index, 2)

            self.value_preview_labels.append(display_label)
            self.value_preview_check_boxes.append(check_box)


class JOANJoystick(BaseInput):
    """
    Main class for the Joystick input, inherits from BaseInput (as it should!)
    """

    def __init__(self, module_action, hardware_input_list_key, settings):
        super().__init__(hardware_input_type = HardwareInputTypes.JOYSTICK, module_action=module_action)
        """
        Initializes the class
        :param hardware_manager_action:
        :param joystick_tab:
        :param settings:
        """

        self.module_action = module_action
        self.hardware_input_list_key = hardware_input_list_key
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

        self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_from_button)
        self._hardware_input_tab.btn_visualization.setEnabled(False)

        self._open_settings_dialog()

    @property
    def get_hardware_input_list_key(self):
        return self.hardware_input_list_key

    def _open_settings_from_button(self):
        """
        Opens the settings dialog from the button on the tab
        :return:
        """
        if self.settings_dialog:
            self.settings_dialog.show()

    def _open_settings_dialog(self):
        """
        Sets the appropriate values for settings but does not actually show the dialog
        :return:
        """
        self.settings_dialog = JoystickSettingsDialog(self.settings)
        self.settings_dialog.accepted.connect(self._open_connection_to_device)

    def _open_connection_to_device(self):
        """
        Starts the connection to a joystick device, sets the boolean 'self._joystick_open' to true if it succeds
        and to false if it fails
        """
        try:
            self._joystick.open(self.settings.device_vendor_id, self.settings.device_product_id)
            self._joystick_open = True
        except OSError:
            print('Connection to USB Joystick failed')  # TODO: move to messagebox
            self._joystick_open = False

    def disable_remove_button(self):
        """
        Disables the remove_input_device joystick button (useful for example when you dont want to be able to remove_input_device an input when the
        simulator is running)
        :return:
        """
        if self._tab_widget.btn_remove_hardware.isEnabled() is True:
            self._tab_widget.btn_remove_hardware.setEnabled(False)
        else:
            pass

    def enable_remove_button(self):
        """
        Enables the remove_input_device joystick button
        :return:
        """
        if self._tab_widget.btn_remove_hardware.isEnabled() is False:
            self._tab_widget.btn_remove_hardware.setEnabled(True)
        else:
            pass

    def do(self):
        """
        Processes all the inputs of the joystick and writes them to self._data which is then written to the news in the
        action class
        :return: self._data a dictionary containing :self._data['brake'] = self.brake
            self._data['throttle'] = self.throttle
            self._data['steering_angle'] = self.steer
            self._data['Handbrake'] = self.handbrake
            self._data['Reverse'] = self.reverse
        """
        if self._joystick_open:
            joystick_data = self._joystick.read(self.settings.degrees_of_freedom, 1)
        else:
            joystick_data = False

        if joystick_data:
            # print(joystick_data)
            if self.settings.use_separate_brake_channel:
                self.throttle = round(((joystick_data[self.settings.gas_channel]) / 255) * 100)
                self.brake = - round(((joystick_data[self.settings.brake_channel]) / 255) * 100)
            else:
                input_value = 100 - round(((joystick_data[self.settings.gas_channel]) / 128) * 100)
                if input_value > 0:
                    self.throttle = input_value
                    self.brake = 0
                elif input_value < 0:
                    self.throttle = 0
                    self.brake = -input_value

            if joystick_data[self.settings.hand_brake_channel] == self.settings.hand_brake_value:
                self.handbrake = True
            elif joystick_data[self.settings.reverse_channel] == self.settings.reverse_value:
                self.reverse = True
            else:
                self.handbrake = False
                self.reverse = False

            if self.settings.use_double_steering_resolution:
                self.steer = round(
                    (((joystick_data[self.settings.first_steer_channel]) + (
                        joystick_data[self.settings.second_steer_channel]) * 256) / (256 * 256)) * (
                            self.settings.max_steer - self.settings.min_steer) - self.settings.max_steer)
            else:
                self.steer = round(
                    ((joystick_data[self.settings.first_steer_channel]) / 255) * (
                            self.settings.max_steer - self.settings.min_steer) - self.settings.max_steer)

        self._data['brake'] = self.brake
        self._data['throttle'] = self.throttle
        self._data['steering_angle'] = self.steer
        self._data['Handbrake'] = self.handbrake
        self._data['Reverse'] = self.reverse

        return self._data
