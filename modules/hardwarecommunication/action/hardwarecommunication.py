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
        self._data['GearShiftInput'] = 0
        self._data['BrakeInput'] = 0
        self._data['Reverse'] = False

        self.currentInput = 'None'

        self.steerRange = 180  # range until
        self.brake = 0
        self.throttle = 0
        self.steer = 0

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

        self._keyboard_tab.btn_remove_hardware.clicked.connect(self.remove_tab)

        self._parentWidget.window.keyPressEvent = self.keyPressEvent
        self._parentWidget.window.keyReleaseEvent = self.keyReleaseEvent
        
        self.steer_left = False
        self.steer_right = False
        self.throttle = False
        self.brake = False
        self.reverse = False

        # Open the settings window:


    def remove_tab(self):
        self._action.remove(self._keyboard_tab.groupBox.title())
        self._parentWidget.widget.hardware_list_layout.removeWidget(self._keyboard_tab)
        self._keyboard_tab.setParent(None)

    def keyPressEvent(self, event):
        if(self.currentInput == 'Keyboard'):
            key = event.key()
            if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_W:
                self.throttle = True
            elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_S:
                self.brake = True
            elif key == QtCore.Qt.Key_A or key == QtCore.Qt.Key_Left:
                self.steer_left = True
                self.steer_right = False
            elif key == QtCore.Qt.Key_D or key == QtCore.Qt.Key_Right:
                self.steer_right = True
                self.steer_left = False

    def keyReleaseEvent(self, event):
        if(self.currentInput == 'Keyboard'):
            key = event.key()
            if key == QtCore.Qt.Key_Up or key == QtCore.Qt.Key_W:
                self.throttle = False
            elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_S:
                self.brake = False
            elif key == QtCore.Qt.Key_A or key == QtCore.Qt.Key_Left:
                self.steer_left = False
                self.steer_right = False
            elif key == QtCore.Qt.Key_D or key == QtCore.Qt.Key_Right:
                self.steer_right = False
                self.steer_left = False
            elif key == QtCore.Qt.Key_R:
                if not self.reverse:
                    self.reverse = True
                elif self.reverse:
                    self.reverse = False

    def setCurrentInput(self):
        self.currentInput = 'Keyboard'
        # self._parentWidget.widget.sliderThrottle.setEnabled(False)
        # self._parentWidget.widget.sliderSteering.setEnabled(False)
        # self._parentWidget.widget.sliderBrake.setEnabled(False)
        self.changeInputSource()

    def displayInputs(self):
        # update sliders and reverse label
        # self._parentWidget.widget.sliderThrottle.setValue(self._data['ThrottleInput'])
        # self._parentWidget.widget.sliderSteering.setValue(self._data['SteeringInput'])
        # self._parentWidget.widget.sliderBrake.setValue(self._data['BrakeInput'])
        # self._parentWidget.widget.lblReverse.setText(str(self.reverse))

        # #set values next to sliders:
        # self._parentWidget.widget.lblThrottle.setText(str(self._data['ThrottleInput']))
        # self._parentWidget.widget.lblSteering.setText(str(self._data['SteeringInput']))
        # self._parentWidget.widget.lblBrake.setText(str(self._data['BrakeInput']))
        pass

    def process(self):
        # Throttle:
        if(self.throttle and self._data['ThrottleInput'] < 100):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] + 2.5
        elif(self._data['ThrottleInput'] > 0 and not self.throttle):
            self._data['ThrottleInput'] = self._data['ThrottleInput'] - 2.5

        # Brake:
        if(self.brake and self._data['BrakeInput'] < 100):
            self._data['BrakeInput'] = self._data['BrakeInput'] + 5
        elif(self._data['BrakeInput'] > 0 and not self.brake):
            self._data['BrakeInput'] = self._data['BrakeInput'] - 5

        # Steering:
        if(self.steer_left and self._data['SteeringInput'] < self.steerRange and self._data['SteeringInput'] > -self.steerRange):
            self._data['SteeringInput'] = self._data['SteeringInput'] - 2
        elif(self.steer_right and self._data['SteeringInput'] > -self.steerRange and self._data['SteeringInput'] < self.steerRange):
            self._data['SteeringInput'] = self._data['SteeringInput'] + 2
        elif(self._data['SteeringInput'] > 0):
            self._data['SteeringInput'] = self._data['SteeringInput'] - 1
        elif(self._data['SteeringInput'] < 0):
            self._data['SteeringInput'] = self._data['SteeringInput'] + 1

        self.displayInputs()

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
        # self._parentWidget.widget.sliderThrottle.setEnabled(True)
        # self._parentWidget.widget.sliderSteering.setEnabled(True)
        # self._parentWidget.widget.sliderBrake.setEnabled(True)
        # self.currentInput = 'Mouse'
        # self.changeInputSource()
        pass

    def process(self):
        # self._data['BrakeInput']    = self._parentWidget.widget.sliderBrake.value()
        # self._data['ThrottleInput'] = self._parentWidget.widget.sliderThrottle.value()
        # self._data['SteeringInput'] = self._parentWidget.widget.sliderSteering.value()
        # self.displayInputs()

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
