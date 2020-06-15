import os

import hid
from PyQt5 import uic, QtWidgets, QtCore

from modules.hardwaremanager.action.hardwaremanagersettings import JoyStickSettings
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.joanmodules import JOANModules


class JoystickSettingsDialog(QtWidgets.QDialog):
    def __init__(self, joystick_settings, parent=None):
        super().__init__(parent)
        self.joystick_settings = joystick_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/joystick_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(self._set_default_settings)

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
        self.show()

    def preview_joystick_values(self):
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
        self.presetsComboBox.setCurrentIndex(0)

    def _set_presets(self):
        if self.presetsComboBox.currentText().lower() != 'custom':
            preset_settings = JoyStickSettings.get_preset_settings(self.presetsComboBox.currentText().lower())
            self._display_settings(settings_to_display=preset_settings, only_keymap=True)

    def _display_settings(self, settings_to_display=None, only_keymap=False):
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
        self._display_settings(JoyStickSettings())

    def _update_brake_channel_enabled(self, value):
        self.brakeChannelSpinBox.setEnabled(value)

    def _update_second_steer_channel_enabled(self, value):
        self.steerSecondChannelSpinBox.setEnabled(value)

    def _enable_preview_checkbox(self):
        if self.combo_available_devices.currentData():
            self.displayCurrentInputCheckBox.setEnabled(True)
        else:
            self.displayCurrentInputCheckBox.setChecked(False)
            self.displayCurrentInputCheckBox.setEnabled(False)

    def _enable_previewing_values(self, value):
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

        self._open_settings_dialog()

    def initialize(self):
        print('initializing Joystick')

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
        if self._carla_interface_data['vehicles'] is not None:
            self._carla_interface_data = self._action.read_news(JOANModules.CARLA_INTERFACE)

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._joystick_tab.groupBox.title():
                    self._joystick_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._joystick_tab.btn_remove_hardware.setEnabled(True)

        if self._joystick_open:
            joystick_data = self._joystick.read(self.settings.degrees_of_freedom, 1)

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
                    (((joystick_data[self.settings.first_steer_channel]) + (joystick_data[self.settings.second_steer_channel]) * 256) / (256 * 256)) * (
                            self.settings.max_steer - self.settings.min_steer) - self.settings.max_steer)
            else:
                self.steer = round(
                    ((joystick_data[self.settings.first_steer_channel]) / 255) * (self.settings.max_steer - self.settings.min_steer) - self.settings.max_steer)

        self._data['BrakeInput'] = self.brake
        self._data['ThrottleInput'] = self.throttle
        self._data['SteeringInput'] = self.steer
        self._data['Handbrake'] = self.handbrake
        self._data['Reverse'] = self.reverse

        return self._data
