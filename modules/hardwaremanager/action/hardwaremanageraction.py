from PyQt5 import QtCore, uic, QtGui
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import HardwaremanagerStates
import os
import hid
import keyboard


class HardwaremanagerAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=5):
        super().__init__(module=JOANModules.HARDWARE_MANAGER, master_state_handler=master_state_handler, millis=millis)

        HardwaremanagerAction.input_devices_classes = {}
        HardwaremanagerAction.input_devices_widgets = {}
        HardwaremanagerAction._nr_of_mouses = 0
        HardwaremanagerAction._nr_of_keyboards = 0
        HardwaremanagerAction._nr_of_joysticks = 0
        HardwaremanagerAction._nr_of_sensodrives = 0
        self._selected_input_device = ''

        self.data = {}
        self.write_news(news=self.data)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        for inputs in HardwaremanagerAction.input_devices_classes:
            self.data[inputs] = HardwaremanagerAction.input_devices_classes[inputs].process()
        self.write_news(self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        pass

    def start(self):
        try:
            self.module_state_handler.request_state_change(HardwaremanagerStates.HARDWARECOMMUNICATION.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(HardwaremanagerStates.HARDWARECOMMUNICATION.STOPPED)
        except RuntimeError:
            return False
        return super().stop()

    def selected_input(self, input_string):
        self._selected_input_device = input_string

        if "Mouse" in self._selected_input_device:
            HardwaremanagerAction._nr_of_mouses = HardwaremanagerAction._nr_of_mouses + 1
            device_title = "Mouse " + str(self._nr_of_mouses)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, JOAN_Mouse(self, self.input_devices_widgets[device_title]))])

        if "Keyboard" in self._selected_input_device:
            HardwaremanagerAction._nr_of_keyboards = HardwaremanagerAction._nr_of_keyboards + 1
            device_title = "Keyboard " + str(self._nr_of_keyboards)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, JOAN_Keyboard(self, self.input_devices_widgets[device_title]))])

        if "Joystick" in self._selected_input_device:
            HardwaremanagerAction._nr_of_joysticks = HardwaremanagerAction._nr_of_joysticks + 1
            device_title = "Joystick " + str(self._nr_of_joysticks)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, JOAN_Joystick(self, self.input_devices_widgets[device_title]))])

        if "SensoDrive" in self._selected_input_device:
            HardwaremanagerAction._nr_of_sensodrives = HardwaremanagerAction._nr_of_sensodrives + 1
            device_title = "SensoDrive " + str(self._nr_of_sensodrives)
            HardwaremanagerAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwaremanagerAction.input_devices_classes.update([(device_title, JOAN_SensoDrive(self, self.input_devices_widgets[device_title]))])

        HardwaremanagerAction.input_devices_widgets[device_title].groupBox.setTitle(device_title)

        return HardwaremanagerAction.input_devices_widgets

        # print(HardwaremanagerAction.input_devices_classes)

    def remove(self, tabtitle):
        if "Keyboard" in tabtitle:
            HardwaremanagerAction._nr_of_keyboards = HardwaremanagerAction._nr_of_keyboards - 1
            keyboard.unhook(HardwaremanagerAction.input_devices_classes[tabtitle].key_event)

        if "Mouse" in tabtitle:
            HardwaremanagerAction._nr_of_mouses = HardwaremanagerAction._nr_of_mouses - 1

        if "Joystick" in tabtitle:
            HardwaremanagerAction._nr_of_joysticks = HardwaremanagerAction._nr_of_joysticks - 1

        if "Sensodrive" in tabtitle:
            HardwaremanagerAction._nr_of_sensodrives = HardwaremanagerAction._nr_of_sensodrives - 1

        del HardwaremanagerAction.input_devices_widgets[tabtitle]
        del HardwaremanagerAction.input_devices_classes[tabtitle]
        del self.data[tabtitle]


class BaseInput:
    def __init__(self, hardware_manager_action):
        self._carla_interface_data = hardware_manager_action.read_news('modules.carlainterface.action.carlainterfaceaction.CarlainterfaceAction')
        self._action = hardware_manager_action
        self._data = {'SteeringInput': 0, 'ThrottleInput': 0, 'BrakeInput': 0, 'Reverse': False, 'Handbrake': False}
        self.currentInput = 'None'

    def remove_tab(self, tab):
        self._action.remove(tab.groupBox.title())
        tab.setParent(None)
        
    def process(self):
        return self._data

class JOAN_Keyboard(BaseInput):
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

        # Initialize keyboard settings
        self._min_steer = 0
        self._max_steer = 0
        self._autocenter = False
        self._steer_sensitivity = 0
        self._brake_sensitivity = 0
        self._throttle_sensitivity = 0
        self._steer_left_key = ''
        self._steer_right_key = ''
        self._throttle_key = ''
        self._brake_key = ''
        self._reverse_key = ''
        self._handbrake_key = ''

        # Load the appropriate settings window and show it:
        self._settings_tab = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/keyboard_settings_ui.ui"))
        self._settings_tab.show()

        # Connect the settings button to the settings window
        self._keyboard_tab.btn_settings.clicked.connect(self._settings_tab.show)

        # Connect the hardware remove button to removing routine
        self._keyboard_tab.btn_remove_hardware.clicked.connect(self.remove_func)

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
        
        keyboard.hook(self.key_event, False)

    def remove_func(self):
        self.remove_tab(self._keyboard_tab)

    def settings_set_default_values(self):
        # Keys
        self._steer_left_key = 'a'
        self._steer_right_key = 'd'
        self._throttle_key = 'w'
        self._brake_key = 's'
        self._reverse_key = 'r'
        self._handbrake_key = 'space'

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
                self._steer_left_key = event.text()
            elif self._set_key_counter == 2:
                self._settings_tab.label_steer_right.setText(text)
                self._settings_tab.label_steer_right.setStyleSheet("background-color: none")
                self._settings_tab.label_throttle.setStyleSheet("background-color: lightgreen")
                self._steer_right_key = event.text()
            elif self._set_key_counter == 3:
                self._settings_tab.label_throttle.setText(text)
                self._settings_tab.label_throttle.setStyleSheet("background-color: none")
                self._settings_tab.label_brake.setStyleSheet("background-color: lightgreen")
                self._throttle_key = event.text()
            elif self._set_key_counter == 4:
                self._settings_tab.label_brake.setText(text)
                self._settings_tab.label_brake.setStyleSheet("background-color: none")
                self._settings_tab.label_reverse.setStyleSheet("background-color: lightgreen")
                self._brake_key = event.text()
            elif self._set_key_counter == 5:
                self._settings_tab.label_reverse.setText(text)
                self._settings_tab.label_reverse.setStyleSheet("background-color: none")
                self._settings_tab.label_handbrake.setStyleSheet("background-color: lightgreen")
                self._reverse_key = event.text()
            elif self._set_key_counter == 6:
                self._settings_tab.label_handbrake.setText(text)
                self._settings_tab.label_handbrake.setStyleSheet("background-color: none")
                self._handbrake_key = event.text()
                self._settings_tab.btn_set_keys.setChecked(False)
                self._settings_tab.btn_set_keys.setStyleSheet("background-color: none")
                self._set_key_counter = 0
                self._settings_tab.button_box_settings.setEnabled(True)
                self._settings_tab.btn_set_keys.setEnabled(True)

    def key_event(self, key):
        if (key.event_type == keyboard.KEY_DOWN):
            if key.name == self._throttle_key:
                self._throttle = True
            elif key.name == self._brake_key:
                self._brake = True
            elif key.name == self._steer_left_key:
                self._steer_left = True
                self._steer_right = False
            elif key.name == self._steer_right_key:
                self._steer_right = True
                self._steer_left = False
            elif key.name == self._handbrake_key:
                self._handbrake = True

        if (key.event_type == keyboard.KEY_UP):
            if key.name == self._throttle_key:
                self._throttle = False
            elif key.name == self._brake_key:
                self._brake = False
            elif key.name == self._steer_left_key:
                self._steer_left = False
                self._steer_right = False
            elif key.name == self._steer_right_key:
                self._steer_right = False
                self._steer_left = False
            elif key.name == self._handbrake_key:
                self._handbrake = False
            elif key.name == self._reverse_key:
                if not self._reverse:
                    self._reverse = True
                elif self._reverse:
                    self._reverse = False

    def process(self):
        # # If there are cars in the simulation add them to the controllable car combobox
        if (self._carla_interface_data['vehicles'] is not None):
            self._carla_interface_data = self._action.read_news('modules.carlainterface.action.carlainterfaceaction.CarlainterfaceAction')

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


class JOAN_Mouse(BaseInput): #DEPRECATED FOR NOW
    def __init__(self, hardware_manager_action, mouse_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Mouse'
        # Add the tab to the widget
        self._mouse_tab = mouse_tab
        self._mouse_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        self.remove_tab(self._mouse_tab)
    
    def process(self):
        if (self._carla_interface_data['vehicles'] is not None):
            # self._carla_interface_data = self._action.read_news('modules.carlainterface.action.carlainterfaceaction.CarlainterfaceAction')

            # for vehicles in self._carla_interface_data['vehicles']:
            #     if vehicles.selected_input == self._mouse_tab.groupBox.title():
            #         self._mouse_tab.btn_remove_hardware.setEnabled(False)
            #         break
            #     else:
            #         self._mouse_tab.btn_remove_hardware.setEnabled(True)

            return self._data


# Arbitratry Joystick
class JOAN_Joystick(BaseInput):
    def __init__(self, hardware_manager_action, joystick_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Joystick'
        self._joystick_tab = joystick_tab
        self._joystick_open = False
        self._joystick_tab.btn_remove_hardware.clicked.connect(self.remove_func)
        self._joystick = hid.device()

        #Initialize Variables
        self._min_steer = 0
        self._max_steer = 0
        self.brake = 0
        self.steer = 0
        self.throttle = 0
        self.handbrake = False
        self.reverse = False

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
            self._carla_interface_data = self._action.read_news('modules.carlainterface.action.carlainterfaceaction.CarlainterfaceAction')

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


class JOAN_SensoDrive(BaseInput): #DEPRECATED FOR NOW
    def __init__(self, hardware_manager_action, sensodrive_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        self.remove_tab(self._sensodrive_tab)
