import os

import keyboard
from PyQt5 import uic

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import HardwaremanagerStates
from modules.hardwaremanager.action.inputclasses.JOAN_keyboard import JOAN_Keyboard
from modules.hardwaremanager.action.inputclasses.JOAN_mouse import JOAN_Mouse
from modules.hardwaremanager.action.inputclasses.JOAN_joystick import JOAN_Joystick
from modules.hardwaremanager.action.inputclasses.JOAN_sensodrive import JOAN_SensoDrive


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
            self.module_state_handler.request_state_change(HardwaremanagerStates.EXEC.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(HardwaremanagerStates.EXEC.STOPPED)
            if len(HardwaremanagerAction.input_devices_classes) != 0:
                self.module_state_handler.request_state_change(HardwaremanagerStates.EXEC.READY)
            
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

        if len(HardwaremanagerAction.input_devices_classes) == 0:
            self.module_state_handler.request_state_change(HardwaremanagerStates.IDLE)

