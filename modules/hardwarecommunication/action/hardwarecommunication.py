from process import Control
from PyQt5 import uic, QtCore, QtGui
import os
import hid


class HardwarecommunicationAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        # get state information from module Widget
        self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or None
        self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None
        HardwarecommunicationAction.input_devices_classes = {}
        HardwarecommunicationAction.input_devices_widgets = {}
        HardwarecommunicationAction._nr_of_mouses = 0
        HardwarecommunicationAction._nr_of_keyboards = 0
        HardwarecommunicationAction._nr_of_joysticks = 0
        HardwarecommunicationAction._nr_of_sensodrives = 0
        

    def selected_input(self):
        self._selected_input_device = self.widget._input_type_dialog.combo_hardware_inputtype.currentText()

        if "Mouse" in self._selected_input_device:
            HardwarecommunicationAction._nr_of_mouses = HardwarecommunicationAction._nr_of_mouses + 1
            device_title = "Mouse " + str(self._nr_of_mouses)
            HardwarecommunicationAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwarecommunicationAction.input_devices_classes.update([(device_title, Mouse(self, self.input_devices_widgets[device_title]))])

        if "Keyboard" in self._selected_input_device:
            HardwarecommunicationAction._nr_of_keyboards = HardwarecommunicationAction._nr_of_keyboards + 1
            device_title = "Keyboard " + str(self._nr_of_keyboards)
            HardwarecommunicationAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwarecommunicationAction.input_devices_classes.update([(device_title, Keyboard(self, self.input_devices_widgets[device_title]))])

        if "Joystick" in self._selected_input_device:
            HardwarecommunicationAction._nr_of_joysticks = HardwarecommunicationAction._nr_of_joysticks + 1
            device_title = "Joystick " + str(self._nr_of_joysticks)
            HardwarecommunicationAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwarecommunicationAction.input_devices_classes.update([(device_title, Joystick(self, self.input_devices_widgets[device_title]))])

        if "SensoDrive" in self._selected_input_device:
            HardwarecommunicationAction._nr_of_sensodrives = HardwarecommunicationAction._nr_of_sensodrives + 1
            device_title = "SensoDrive " + str(self._nr_of_sensodrives)
            HardwarecommunicationAction.input_devices_widgets.update(
                [(device_title, uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/hardware_tab.ui")))])
            HardwarecommunicationAction.input_devices_classes.update([(device_title, SensoDrive(self, self.input_devices_widgets[device_title]))])

        HardwarecommunicationAction.input_devices_widgets[device_title].groupBox.setTitle(device_title)

        print(HardwarecommunicationAction.input_devices_classes)

    def remove(tabtitle):
        del HardwarecommunicationAction.input_devices_widgets[tabtitle]
        del HardwarecommunicationAction.input_devices_classes[tabtitle]

        if "Keyboard" in tabtitle:
            HardwarecommunicationAction._nr_of_keyboards = HardwarecommunicationAction._nr_of_keyboards - 1

        if "Mouse" in tabtitle:
            HardwarecommunicationAction._nr_of_mouses = HardwarecommunicationAction._nr_of_mouses - 1

        if "Joystick" in tabtitle:
            HardwarecommunicationAction._nr_of_joysticks = HardwarecommunicationAction._nr_of_joysticks - 1

        if "Sensodrive" in tabtitle:
            HardwarecommunicationAction._nr_of_sensodrives = HardwarecommunicationAction._nr_of_sensodrives - 1

        print(HardwarecommunicationAction.input_devices_classes)


class BaseInput():
    def __init__(self, HardwarecommunicationWidget, HardwarecommunicationAction):
        self._parentWidget = HardwarecommunicationWidget.widget
        self._action = HardwarecommunicationAction
        self._data = {}
        self._data['SteeringInput'] = 0
        self._data['ThrottleInput'] = 0
        self._data['BrakeInput'] = 0
        self._data['Reverse'] = False
        self._data['Handbrake'] = False

        self.currentInput = 'None'

        #self._carla_interface_data = {}

        # #already list the input devices here:
        # for self._devices in hid.enumerate():
        #     keys = list(self._devices.keys())
        #     keys.sort()
        #     for key in keys:
        #         print("%s : %s" % (key, self._devices[key]))
        #     print()

    def process(self):
        return self._data

    def changeInputSource(self):
        pass

    def setUsingtext(self):
        pass

    def displayInputs(self):
        pass


class Keyboard(BaseInput):
    def __init__(self, HardwarecommunicationWidget, keyboard_tab):
        BaseInput.__init__(self, HardwarecommunicationWidget, HardwarecommunicationAction)
        self._keyboard_tab = keyboard_tab
        self._parentWidget.widget.hardware_list_layout.addWidget(self._keyboard_tab)

        self._carla_interface_data = {}

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
        self._keyboard_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

        # Connect buttons of settings menu to methods:
        self._settings_tab.btn_set_keys.clicked.connect(self.settings_set_keys)
        self._settings_tab.button_box_settings.button(self._settings_tab.button_box_settings.RestoreDefaults).clicked.connect(self.settings_set_default_values)
        self._settings_tab.keyPressEvent = self.settings_key_press_event
        self._settings_tab.slider_steer_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._settings_tab.slider_throttle_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._settings_tab.slider_brake_sensitivity.valueChanged.connect(self.settings_update_sliders)
        self._set_key_counter = 0

        # set the default settings when constructing:
        self.settings_set_default_values()

        # Overwriting keypress events to handle keypresses for controlling
        self._parentWidget.window.keyPressEvent = self.key_press_event
        self._parentWidget.window.keyReleaseEvent = self.key_release_event

    def settings_update_sliders(self):
        self._settings_tab.label_steer_sensitivity.setText(str(self._settings_tab.slider_steer_sensitivity.value()))
        self._settings_tab.label_throttle_sensitivity.setText(str(self._settings_tab.slider_throttle_sensitivity.value()))
        self._settings_tab.label_brake_sensitivity.setText(str(self._settings_tab.slider_brake_sensitivity.value()))

    def settings_set_default_values(self):
        # Keys
        self._steer_left_key = QtCore.Qt.Key_A
        self._steer_right_key = QtCore.Qt.Key_D
        self._throttle_key = QtCore.Qt.Key_W
        self._brake_key = QtCore.Qt.Key_S
        self._reverse_key = QtCore.Qt.Key_R
        self._handbrake_key = QtCore.Qt.Key_K

        #Key Names
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

        # Nr vehicles
        self.old_nr_vehicles = 0

    def settings_set_keys(self):
        self._settings_tab.btn_set_keys.setStyleSheet("background-color: lightgreen")
        self._settings_tab.btn_set_keys.clearFocus()
        self._settings_tab.button_box_settings.setEnabled(False)
        self._settings_tab.btn_set_keys.setEnabled(False)
        self._set_key_counter = 0
        self._settings_tab.label_steer_left.setStyleSheet("background-color: lightgreen")

    def settings_key_press_event(self,event):
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
        self._parentWidget.widget.hardware_list_layout.removeWidget(self._keyboard_tab)
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
        # If there are cars in the simulation add them to the controllable car combobox
        self._carla_interface_data = (self._parentWidget.readNews('modules.carlainterface.widget.carlainterface.CarlainterfaceWidget'))
        for items in self._carla_interface_data['vehicles']:
            print(items.spawned)
    
  
        
        # new_nr_vehicles = len(self._carla_interface_data['vehicles'])
        # if (new_nr_vehicles - self.old_nr_vehicles > 0):
        #     latest_id = self._carla_interface_data['vehicles'][-1].get_vehicle_id()
        #     self._keyboard_tab.combo_target_vehicle.addItem(latest_id)

        # if (new_nr_vehicles - self.old_nr_vehicles < 0):
        #     self._keyboard_tab.combo_target_vehicle.removeItem(new_nr_vehicles-1)

        
        

        # Throttle:
        if(self._throttle and self._data['ThrottleInput'] < 100):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] + (5 * self._throttle_sensitivity/100)
        elif(self._data['ThrottleInput'] > 0 and not self._throttle):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] - (5 * self._throttle_sensitivity/100)

        # Brake:
        if(self._brake and self._data['BrakeInput'] < 100):
            self._data['BrakeInput'] = self._data['BrakeInput'] + (5 * self._brake_sensitivity/100)
        elif(self._data['BrakeInput'] > 0 and not self._brake):
            self._data['BrakeInput'] = self._data['BrakeInput'] - (5 * self._brake_sensitivity/100)

        # Steering:
        if(self._steer_left and self._data['SteeringInput'] < self._max_steer and self._data['SteeringInput'] > self._min_steer):
            self._data['SteeringInput'] = self._data['SteeringInput'] - (4 * self._steer_sensitivity/100)
        elif(self._steer_right and self._data['SteeringInput'] > self._min_steer and self._data['SteeringInput'] < self._max_steer):
            self._data['SteeringInput'] = self._data['SteeringInput'] + (4 * self._steer_sensitivity/100)
        elif(self._data['SteeringInput'] > 0 and self._autocenter):
            self._data['SteeringInput'] = self._data['SteeringInput'] - (2 * self._steer_sensitivity/100)
        elif(self._data['SteeringInput'] < 0 and self._autocenter):
            self._data['SteeringInput'] = self._data['SteeringInput'] + (2 * self._steer_sensitivity/100)

        # Reverse
        self._data['Reverse'] = self._reverse

        # Handbrake
        self._data['Handbrake'] = self._handbrake

        # self.old_nr_vehicles = new_nr_vehicles
        return self._data


class Mouse(BaseInput):
    def __init__(self, HardwarecommunicationWidget, mouse_tab):
        BaseInput.__init__(self, HardwarecommunicationWidget, HardwarecommunicationAction)
        self.currentInput = 'Mouse'
        # Add the tab to the widget
        self._mouse_tab = mouse_tab
        self._parentWidget.widget.hardware_list_layout.addWidget(self._mouse_tab)

        self._mouse_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

    def remove_tab(self):
        self._action.remove(self._mouse_tab.groupBox.title())
        self._parentWidget.widget.hardware_list_layout.removeWidget(self._mouse_tab)
        self._mouse_tab.setParent(None)

    def displayInputs(self):
        pass

    def setCurrentInput(self):

        pass

    def process(self):
        return self._data

# Arbitratry Joystick
class Joystick(BaseInput):
    def __init__(self, HardwarecommunicationWidget, joystick_tab):
        BaseInput.__init__(self, HardwarecommunicationWidget, HardwarecommunicationAction)
        self.currentInput = 'Joystick'
        self._joystick_tab = joystick_tab
        self._parentWidget.widget.hardware_list_layout.addWidget(self._joystick_tab)

        self._joystick_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

        # self._joystickTab.btnUse.clicked.connect(self.setCurrentInput)

        # Open the desired device to read (find the device and vendor ID from printed list!!)
        self._joystick = hid.device()

        # Initialize Variables
        self.steer = 0
        self.throttle = 0
        self.brake = 0

        try:
            # self._joystick.open(121, 6) #  Playstation controller Zierikzee (vendor,product)
            # self._joystick.open(1133, 49760) #logitech wheel CoRlab
            # self._joystick.open(16700, 8467) #Taranis Zierikzee
            self._joystick.open(1118, 736)
        except:
            print('Could not open joystick. Is it plugged in? Are the IDs correct?')

    def remove_tab(self):
        self._action.remove(self._joystick_tab.groupBox.title())
        self._parentWidget.widget.hardware_list_layout.removeWidget(self._joystick_tab)
        self._joystick_tab.setParent(None)

    def displayInputs(self):
        # update sliders
        # self._parentWidget.widget.sliderThrottle.setValue(self._data['ThrottleInput'])
        # self._parentWidget.widget.sliderSteering.setValue(self._data['SteeringInput'])
        # self._parentWidget.widget.sliderBrake.setValue(self._data['BrakeInput'])

        # set values next to sliders:
        # self._parentWidget.widget.lblThrottle.setText(str(self._data['ThrottleInput']))
        # self._parentWidget.widget.lblSteering.setText(str(self._data['SteeringInput']))
        # self._parentWidget.widget.lblBrake.setText(str(self._data['BrakeInput']))
        pass

    def setCurrentInput(self):
        # self._parentWidget.widget.sliderThrottle.setEnabled(False)
        # self._parentWidget.widget.sliderSteering.setEnabled(False)
        # self._parentWidget.widget.sliderBrake.setEnabled(False)
        self.currentInput = 'Joystick'
        self.changeInputSource()

    def process(self):
        joystickdata = []
        joystickdata = self._joystick.read(64, 64)

        if joystickdata != []:
            self.throttle = 100 - round((((joystickdata[9])/128))*100)
            if joystickdata[10] == 2:
                self.brake = 80
            else:
                self.brake = 0

            self.steer = round((((joystickdata[0]) + (joystickdata[1])*256)/(256*256))*180 - 90)
            print(joystickdata)
        self._data['BrakeInput'] = self.brake
        self._data['ThrottleInput'] = self.throttle
        self._data['SteeringInput'] = self.steer

        self.displayInputs()

        return self._data


class SensoDrive(BaseInput):
    def __init__(self, HardwarecommunicationWidget, sensodrive_tab):
        BaseInput.__init__(self, HardwarecommunicationWidget, HardwarecommunicationAction)
        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self._parentWidget.widget.hardware_list_layout.addWidget(self._sensodrive_tab)

        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

    def remove_tab(self):
        self._action.remove(self._sensodrive_tab.groupBox.title())
        self._parentWidget.widget.hardware_list_layout.removeWidget(self._sensodrive_tab)
        self._sensodrive_tab.setParent(None)
