from PyQt5 import QtCore, uic, QtGui
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import HardwaremanagerStates
import os
import hid


class HardwaremanagerAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=2):
        super().__init__(module=JOANModules.HARDWARE_MANAGER, master_state_handler=master_state_handler, millis=millis)

        HardwaremanagerAction.input_devices_classes = {}
        HardwaremanagerAction.input_devices_widgets = {}
        HardwaremanagerAction._nr_of_mouses = 0
        HardwaremanagerAction._nr_of_keyboards = 0
        HardwaremanagerAction._nr_of_joysticks = 0
        HardwaremanagerAction._nr_of_sensodrives = 0
        self.data = {}

        self.write_news(news=self.data)
        self.time = QtCore.QTime()

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        for inputs in HardwaremanagerAction.input_devices_classes:
            self.data[inputs] = HardwaremanagerAction.input_devices_classes[inputs].process()
            print(self.data)
        self.write_news(self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        pass

    def start(self):
        try:
            self.module_state_handler.request_state_change(HardwaremanagerStates.HARDWARECOMMUNICATION.RUNNING)
            self.time.restart()
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(HardwaremanagerStates.HARDWARECOMMUNICATION.STOPPED)
        except RuntimeError:
            return False
        return super().start()

    def selected_input(self, input_string):
        self._selected_input_device = input_string

        if "Mouse" in self._selected_input_device:
            HardwaremanagerAction._nr_of_mouses = HardwaremanagerAction._nr_of_mouses + 1
            device_title = "Mouse " + str(self._nr_of_mouses)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, Mouse(self, self.input_devices_widgets[device_title]))])

        if "Keyboard" in self._selected_input_device:
            HardwaremanagerAction._nr_of_keyboards = HardwaremanagerAction._nr_of_keyboards + 1
            device_title = "Keyboard " + str(self._nr_of_keyboards)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, Keyboard(self, self.input_devices_widgets[device_title]))])

        if "Joystick" in self._selected_input_device:
            HardwaremanagerAction._nr_of_joysticks = HardwaremanagerAction._nr_of_joysticks + 1
            device_title = "Joystick " + str(self._nr_of_joysticks)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, Joystick(self, self.input_devices_widgets[device_title]))])

        if "SensoDrive" in self._selected_input_device:
            HardwaremanagerAction._nr_of_sensodrives = HardwaremanagerAction._nr_of_sensodrives + 1
            device_title = "SensoDrive " + str(self._nr_of_sensodrives)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, SensoDrive(self, self.input_devices_widgets[device_title]))])

        HardwaremanagerAction.input_devices_widgets[device_title].groupBox.setTitle(device_title)

        return HardwaremanagerAction.input_devices_widgets

        # print(HardwaremanagerAction.input_devices_classes)

    def remove(self, tabtitle):
        del HardwaremanagerAction.input_devices_widgets[tabtitle]
        del HardwaremanagerAction.input_devices_classes[tabtitle]

        if "Keyboard" in tabtitle:
            HardwaremanagerAction._nr_of_keyboards = HardwaremanagerAction._nr_of_keyboards - 1

        if "Mouse" in tabtitle:
            HardwaremanagerAction._nr_of_mouses = HardwaremanagerAction._nr_of_mouses - 1

        if "Joystick" in tabtitle:
            HardwaremanagerAction._nr_of_joysticks = HardwaremanagerAction._nr_of_joysticks - 1

        if "Sensodrive" in tabtitle:
            HardwaremanagerAction._nr_of_sensodrives = HardwaremanagerAction._nr_of_sensodrives - 1

        # print(HardwaremanagerAction.input_devices_classes)


class BaseInput:
    def __init__(self, hardware_manager_action):
        self._carla_interface_data = hardware_manager_action.read_news('modules.carlainterface.action.carlainterfaceaction.CarlainterfaceAction')
        #print(self._carla_interface_data)
        self._action = hardware_manager_action
        self._data = {'SteeringInput': 0, 'ThrottleInput': 0, 'BrakeInput': 0, 'Reverse': False, 'Handbrake': False}

        self.currentInput = 'None'

    def process(self):
        return self._data

    def changeInputSource(self):
        pass

    def setUsingtext(self):
        pass

    def displayInputs(self):
        pass


class Keyboard(BaseInput):
    def __init__(self, hardware_manager_action, keyboard_tab):
        super().__init__(hardware_manager_action)
        self._keyboard_tab = keyboard_tab
        self.hardware_manager_action = hardware_manager_action
        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False

        # nr vehicles
        self._spawned_list = [None] * 10
        self._already_added = [None] * 10
        self.k = 0
        self.i = 0

        # Load the appropriate settings window and show it:
        self._settings_tab = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/keyboard_settings_ui.ui"))
        self._settings_tab.show()

        # Connect the settings button to the settings window
        self._keyboard_tab.btn_settings.clicked.connect(self._settings_tab.show)

        # Connect the hardware remove button to removing routine
        self._keyboard_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

        # Connect buttons of settings menu to methods:
        self._settings_tab.btn_set_keys.clicked.connect(self.settings_set_keys)
        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.RestoreDefaults).clicked.connect(self.settings_set_default_values)
        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.Save).clicked.connect(self.settings_set_newvalues)
        self._settings_tab.keyPressEvent = self.settings_key_press_event
        self._settings_tab.slider_steer_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._settings_tab.slider_throttle_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._settings_tab.slider_brake_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._set_key_counter = 0

        # set the default settings when constructing:
        self.settings_set_default_values()

        # Overwriting keypress events to handle keypresses for controlling
        # self._parentWidget.window.keyPressEvent = self.key_press_event
        # self._parentWidget.window.keyReleaseEvent = self.key_release_event

    def settings_update_sliders(self):
        self._settings_tab.label_steer_sensitivity.setText(str(self._settings_tab.slider_steer_sensitivity.value()))
        self._settings_tab.label_throttle_sensitivity.setText(str(self._settings_tab.slider_throttle_sensitivity.value()))
        self._settings_tab.label_brake_sensitivity.setText(str(self._settings_tab.slider_brake_sensitivity.value()))

    def settings_set_newvalues(self):
        self._min_steer = int(self._settings_tab.line_edit_min_steer.text())
        self._max_steer = int(self._settings_tab.line_edit_max_steer.text())
        self._autocenter = self._settings_tab.checkbox_autocenter.isChecked()
        self._steer_sensitivity = self._settings_tab.slider_steer_sensitivity.value()
        self._brake_sensitivity = self._settings_tab.slider_brake_sensitivity.value()
        self._throttle_sensitivity = self._settings_tab.slider_throttle_sensitivity.value()

    def settings_set_default_values(self):
        # Keys
        self._steer_left_key = QtCore.Qt.Key_A
        self._steer_right_key = QtCore.Qt.Key_D
        self._throttle_key = QtCore.Qt.Key_W
        self._brake_key = QtCore.Qt.Key_S
        self._reverse_key = QtCore.Qt.Key_R
        self._handbrake_key = QtCore.Qt.Key_K

        # Key Names
        self._settings_tab.label_steer_left.setText("A")
        self._settings_tab.label_steer_right.setText("D")
        self._settings_tab.label_throttle.setText("W")
        self._settings_tab.label_brake.setText("S")
        self._settings_tab.label_reverse.setText("R")
        self._settings_tab.label_handbrake.setText("K")

        # Steering Range
        self._min_steer = -90
        self._max_steer = 90

        self._settings_tab.line_edit_min_steer.setText(str(self._min_steer))
        self._settings_tab.line_edit_max_steer.setText(str(self._max_steer))

        # Check autocenter
        self._autocenter = True
        self._settings_tab.checkbox_autocenter.setChecked(self._autocenter)

        # Sensitivities
        self._steer_sensitivity = 50
        self._throttle_sensitivity = 50
        self._brake_sensitivity = 50

        self._settings_tab.slider_steer_sensitivity.setValue(self._steer_sensitivity)
        self._settings_tab.slider_throttle_sensitivity.setValue(self._throttle_sensitivity)
        self._settings_tab.slider_brake_sensitivity.setValue(self._brake_sensitivity)

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
                self._steer_left_key = event.key()
            elif self._set_key_counter == 2:
                self._settings_tab.label_steer_right.setText(text)
                self._settings_tab.label_steer_right.setStyleSheet("background-color: none")
                self._settings_tab.label_throttle.setStyleSheet("background-color: lightgreen")
                self._steer_right_key = event.key()
            elif self._set_key_counter == 3:
                self._settings_tab.label_throttle.setText(text)
                self._settings_tab.label_throttle.setStyleSheet("background-color: none")
                self._settings_tab.label_brake.setStyleSheet("background-color: lightgreen")
                self._throttle_key = event.key()
            elif self._set_key_counter == 4:
                self._settings_tab.label_brake.setText(text)
                self._settings_tab.label_brake.setStyleSheet("background-color: none")
                self._settings_tab.label_reverse.setStyleSheet("background-color: lightgreen")
                self.brake_key = event.key()
            elif self._set_key_counter == 5:
                self._settings_tab.label_reverse.setText(text)
                self._settings_tab.label_reverse.setStyleSheet("background-color: none")
                self._settings_tab.label_handbrake.setStyleSheet("background-color: lightgreen")
                self._reverse_key = event.key()
            elif self._set_key_counter == 6:
                self._settings_tab.label_handbrake.setText(text)
                self._settings_tab.label_handbrake.setStyleSheet("background-color: none")
                self._handbrake_key = event.key()
                self._settings_tab.btn_set_keys.setChecked(False)
                self._settings_tab.btn_set_keys.setStyleSheet("background-color: none")
                self._set_key_counter = 0
                self._settings_tab.button_box_settings.setEnabled(True)
                self._settings_tab.btn_set_keys.setEnabled(True)

    def remove_tab(self):
        self._action.remove(self._keyboard_tab.groupBox.title())
        self._keyboard_tab.setParent(None)

    def key_press_event(self, event):
        key = event.key()
        if key == self._throttle_key:
            self._throttle = True
        elif key == self._brake_key:
            self._brake = True
        elif key == self._steer_left_key:
            self._steer_left = True
            self._steer_right = False
        elif key == self._steer_right_key:
            self._steer_right = True
            self._steer_left = False
        elif key == self._handbrake_key:
            self._handbrake = True

    def key_release_event(self, event):
        key = event.key()
        if key == self._throttle_key:
            self._throttle = False
        elif key == self._brake_key:
            self._brake = False
        elif key == self._steer_left_key:
            self._steer_left = False
            self._steer_right = False
        elif key == self._steer_right_key:
            self._steer_right = False
            self._steer_left = False
        elif key == self._handbrake_key:
            self._handbrake = False
        elif key == self._reverse_key:
            if not self._reverse:
                self._reverse = True
            elif self._reverse:
                self._reverse = False

    def process(self):
        # # If there are cars in the simulation add them to the controllable car combobox
        if (self._carla_interface_data['vehicles'] is not None):
            self._carla_interface_data = self._action.read_news('modules.carlainterface.dialog.carlainterfacedialog.CarlainterfaceDialog')
            #print(self._carla_interface_data)

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._keyboard_tab.groupBox.title():
                    self._keyboard_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._keyboard_tab.btn_remove_hardware.setEnabled(True)

        # Throttle:
        if (self._throttle and self._data['ThrottleInput'] < 100):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] + (5 * self._throttle_sensitivity / 100)
        elif (self._data['ThrottleInput'] > 0 and not self._throttle):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] - (5 * self._throttle_sensitivity / 100)

        # Brake:
        if (self._brake and self._data['BrakeInput'] < 100):
            self._data['BrakeInput'] = self._data['BrakeInput'] + (5 * self._brake_sensitivity / 100)
        elif (self._data['BrakeInput'] > 0 and not self._brake):
            self._data['BrakeInput'] = self._data['BrakeInput'] - (5 * self._brake_sensitivity / 100)

        # Steering:
        if (self._steer_left and self._data['SteeringInput'] < self._max_steer and self._data['SteeringInput'] > self._min_steer):
            self._data['SteeringInput'] = self._data['SteeringInput'] - (4 * self._steer_sensitivity / 100)
        elif (self._steer_right and self._data['SteeringInput'] > self._min_steer and self._data['SteeringInput'] < self._max_steer):
            self._data['SteeringInput'] = self._data['SteeringInput'] + (4 * self._steer_sensitivity / 100)
        elif (self._data['SteeringInput'] > 0 and self._autocenter):
            self._data['SteeringInput'] = self._data['SteeringInput'] - (2 * self._steer_sensitivity / 100)
        elif (self._data['SteeringInput'] < 0 and self._autocenter):
            self._data['SteeringInput'] = self._data['SteeringInput'] + (2 * self._steer_sensitivity / 100)

        # Reverse
        self._data['Reverse'] = self._reverse

        # Handbrake
        self._data['Handbrake'] = self._handbrake

        return self._data


class Mouse(BaseInput):
    def __init__(self, hardware_manager_action, mouse_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Mouse'
        # Add the tab to the widget
        self._mouse_tab = mouse_tab
        # self._parentWidget.widget.hardware_list_layout.addWidget(self._mouse_tab)

        self._mouse_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

    def remove_tab(self):
        self._action.remove(self._mouse_tab.groupBox.title())
        self._mouse_tab.setParent(None)

    def displayInputs(self):
        pass

    def setCurrentInput(self):

        pass

    def process(self):
        if (self._carla_interface_data['vehicles'] is not None):
            self._carla_interface_data = self._parentWidget.read_news('modules.carlainterface.dialog.carlainterfacedialog.CarlainterfaceDialog')

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._mouse_tab.groupBox.title():
                    self._mouse_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._mouse_tab.btn_remove_hardware.setEnabled(True)

            return self._data


# Arbitratry Joystick
class Joystick(BaseInput):
    def __init__(self, hardware_manager_action, joystick_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Joystick'
        self._joystick_tab = joystick_tab
        # self._parentWidget.widget.hardware_list_layout.addWidget(self._joystick_tab)

        self._joystick_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

        self._joystick = hid.device()

        # Load the appropriate settings tab and show it:
        self._settings_tab = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/joystick_settings_ui.ui"))
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

        self._joystick.open(chosen_device['vendor_id'], chosen_device['product_id'])

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

    def remove_tab(self):
        self._action.remove(self._joystick_tab.groupBox.title())
        self._joystick_tab.setParent(None)

    def process(self):
        if (self._carla_interface_data['vehicles'] is not None):
            self._carla_interface_data = self._action.read_news('modules.carlainterface.dialog.carlainterfacedialog.CarlainterfaceDialog')

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._joystick_tab.groupBox.title():
                    self._joystick_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._joystick_tab.btn_remove_hardware.setEnabled(True)

        joystickdata = []
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


class SensoDrive(BaseInput):
    def __init__(self, hardware_manager_action, sensodrive_tab):
        super().__init__(hardware_manager_action)
        self._sensodrive_tab = sensodrive_tab
    #     BaseInput.__init__(self, HardwaremanagerWidget, HardwaremanagerAction)
    #     self.currentInput = 'SensoDrive'
    #     self._sensodrive_tab = sensodrive_tab
    #     self._parentWidget.widget.hardware_list_layout.addWidget(self._sensodrive_tab)
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

    def remove_tab(self):
        self._action.remove(self._sensodrive_tab.groupBox.title())
        self._sensodrive_tab.setParent(None)
    #     self._parentWidget.do()
    #     self._action.remove(self._sensodrive_tab.groupBox.title())
    #     self._parentWidget.widget.hardware_list_layout.removeWidget(self._sensodrive_tab)
    #     self._sensodrive_tab.setParent(None)

    # def process(self):
    #     if(self._carla_interface_data['vehicles'] is not None):
    #         for vehicles in self._carla_interface_data['vehicles']:
    #             if vehicles.selected_input == self._sensodrive_tab.groupBox.title():
    #                 self._sensodrive_tab.btn_remove_hardware.setEnabled(False)
    #                 break
    #             else:
    #                 self._sensodrive_tab.btn_remove_hardware.setEnabled(True)

    #     return self._data
