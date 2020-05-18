import os

import keyboard

from modules.hardwaremanager.action.inputclasses.JOAN_joystick import JOAN_Joystick
from modules.hardwaremanager.action.inputclasses.JOAN_keyboard import JOAN_Keyboard
from modules.hardwaremanager.action.inputclasses.JOAN_sensodrive import JOAN_SensoDrive

from modules.hardwaremanager.action.settings import KeyBoardSettings, JoyStickSettings, SensoDriveSettings,  HardWareManagerSettings
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.settings import ModuleSettings
from .states import HardwaremanagerStates


class HardwaremanagerAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=5):
        super().__init__(module=JOANModules.HARDWARE_MANAGER, master_state_handler=master_state_handler, millis=millis)

        self.input_devices_classes = {}

        self.data = {}
        self.write_news(news=self.data)

        self.settings = HardWareManagerSettings()
        self.module_settings_object = ModuleSettings(file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'hardware_settings.json'))
        loaded_dict = self.module_settings_object.read_settings()

        if bool(loaded_dict['data']):
            self.settings.set_from_loaded_dict(loaded_dict['data'][str(JOANModules.HARDWARE_MANAGER)])

        self.update_settings(self.settings.as_dict())

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        for inputs in self.input_devices_classes:
            self.data[inputs] = self.input_devices_classes[inputs].process()
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
            if len(self.input_devices_classes) != 0:
                self.module_state_handler.request_state_change(HardwaremanagerStates.EXEC.READY)

        except RuntimeError:
            return False
        return super().stop()

    def load_settings_from_file(self, settings_file_to_load):
        self.module_settings_object = ModuleSettings(file=settings_file_to_load)
        loaded_dict = self.module_settings_object.read_settings()

        if bool(loaded_dict['data']):
            self.settings.set_from_loaded_dict(loaded_dict['data'][str(JOANModules.HARDWARE_MANAGER)])
            self.update_settings(self.settings.as_dict())

    def save_settings_to_file(self, file_to_save_in):
        self.module_settings_object = ModuleSettings(file=file_to_save_in)
        self.module_settings_object.write_settings(item={'data': self.settings.as_dict()})

    def add_a_keyboard(self, widget, keyboard_settings=None):
        is_a_new_keyboard = not keyboard_settings
        if is_a_new_keyboard:
            keyboard_settings = KeyBoardSettings()

        number_of_keyboards = sum([bool("Keyboard" in k) for k in self.input_devices_classes.keys()])
        device_title = "Keyboard %s" % (number_of_keyboards + 1)
        self.input_devices_classes.update([(device_title, JOAN_Keyboard(self, widget, keyboard_settings))])
        if is_a_new_keyboard:
            self.settings.key_boards.append(keyboard_settings)
        return device_title

    def add_a_joystick(self, widget, joystick_settings=None):
        is_a_new_joystick = not joystick_settings
        if is_a_new_joystick:
            joystick_settings = JoyStickSettings()

        number_of_joysticks = sum([bool("Joystick" in k) for k in self.input_devices_classes.keys()])
        device_title = "Joystick %s" % (number_of_joysticks + 1)

        self.input_devices_classes.update([(device_title, JOAN_Joystick(self, widget, joystick_settings))])
        if is_a_new_joystick:
            self.settings.joy_sticks.append(joystick_settings)
        return device_title

    def add_a_sensodrive(self, widget, sensodrive_settings=None):
        is_a_new_sensodrive = not sensodrive_settings
        if is_a_new_sensodrive:
            sensodrive_settings = SensoDriveSettings()

        number_of_sensodrives = sum([bool("SensoDrive" in k) for k in self.input_devices_classes.keys()])
        device_title = "Sensodrive %s" % (number_of_sensodrives + 1)

        self.input_devices_classes.update([(device_title, JOAN_SensoDrive(self, widget, sensodrive_settings))])
        if is_a_new_sensodrive:
            self.settings.sensodrives.append(sensodrive_settings)
        return device_title

    def remove(self, tabtitle):
        if "Keyboard" in tabtitle:
            keyboard.unhook(self.input_devices_classes[tabtitle].key_event)

        del self.input_devices_classes[tabtitle]

        try:
            del self.data[tabtitle]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        if not self.input_devices_classes:
            self.stop()
            # self.module_state_handler.request_state_change(HardwaremanagerStates.IDLE)
