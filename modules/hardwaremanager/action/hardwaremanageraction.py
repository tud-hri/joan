import os

import keyboard

from modules.hardwaremanager.action.hardwaremanagersettings import KeyBoardSettings, JoyStickSettings, \
    SensoDriveSettings, HardwareManagerSettings
from modules.hardwaremanager.action.inputclasses.joanjoystick import JOANJoystick
from modules.hardwaremanager.action.inputclasses.joankeyboard import JOANKeyboard
from modules.hardwaremanager.action.inputclasses.joansensodrive import JOANSensoDrive
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State


class HardwareManagerAction(JoanModuleAction):
    """
    HardwareManagerAction is the 'brains' of the module and does most of the calculations and data handling regarding the hardware. Inherits
    from JoanModuleAction.
    """

    def __init__(self, millis=5):
        """
        Initializes the class
        :param millis: the interval in milliseconds that the module will tick at
        """
        super().__init__(module=JOANModules.HARDWARE_MANAGER, millis=millis)

        # Initialize dicts and variables
        self.input_devices_classes = {}
        self.data = {}
        self.write_news(news=self.data)

        self.carla_interface_data = self.read_news(JOANModules.CARLA_INTERFACE)
        self.settings = HardwareManagerSettings(module_enum=JOANModules.HARDWARE_MANAGER)
        self.settings.before_load_settings.connect(self.prepare_load_settings)
        self.settings.load_settings_done.connect(self.apply_loaded_settings)
        self.share_settings(self.settings)

        self.state_machine.add_state_change_listener(self._state_change_listener)

    def _state_change_listener(self):
        """
        Listens to any state change of the module, whenever the state changes this will be executed.
        :return:
        """
        for inputs in self.input_devices_classes:
            self.data[inputs] = self.input_devices_classes[inputs].do()

        for inputs in self.input_devices_classes:
            if self.state_machine.current_state == State.READY or self.state_machine.current_state == State.IDLE:
                self.input_devices_classes[inputs].enable_remove_button()
            else:
                self.input_devices_classes[inputs].disable_remove_button()
        self.write_news(self.data)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        self.carla_interface_data = self.read_news(JOANModules.CARLA_INTERFACE)
        self.carla_interface_status = self.singleton_status.get_module_current_state(JOANModules.CARLA_INTERFACE)

        self.sw_controller_data = self.read_news(JOANModules.STEERING_WHEEL_CONTROL)

        for inputs in self.input_devices_classes:
            self.data[inputs] = self.input_devices_classes[inputs].do()
            if 'SensoDrive' in inputs:
                self.input_devices_classes[inputs]._toggle_on_off(self.carla_interface_data['connected'])

        self.write_news(self.data)

    def initialize(self):
        """
        This function is called before the module is started and will try to initialize any added hardware inputs
        """
        try:
            if self.state_machine.current_state == State.IDLE:
                if len(self.input_devices_classes) != 0:
                    for input_device in self.input_devices_classes:
                        self.input_devices_classes[input_device].initialize()
                        self.state_machine.request_state_change(State.READY, '')
                        for inputs in self.input_devices_classes:
                            self.data[inputs] = self.input_devices_classes[inputs].do()
                else:
                    self.state_machine.request_state_change(State.ERROR, 'No hardware to Initialize')
            elif self.state_machine.current_state == State.ERROR:
                self.state_machine.request_state_change(State.IDLE)

        except RuntimeError:
            return False
        return super().initialize()

    def start(self):
        """
        Starts the module, which will start running in the 'millis' interval, will go from state ready to running
        :return:
        """
        self.carla_interface_data = self.read_news(JOANModules.CARLA_INTERFACE)
        # make sure you can only turn on the motor of the wheel if carla is connected
        for inputs in self.input_devices_classes:
            if 'SensoDrive' in inputs:
                self.input_devices_classes[inputs]._toggle_on_off(self.carla_interface_data['connected'])

        try:
            self.state_machine.request_state_change(State.RUNNING, 'Hardware manager running')

        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        """
        Stops the module, and will go from state running to ready
        :return:
        """
        self.carla_interface_data = self.read_news(JOANModules.CARLA_INTERFACE)
        for inputs in self.input_devices_classes:
            if 'SensoDrive' in inputs:
                self.input_devices_classes[inputs]._tab_widget.btn_on_off.setStyleSheet("background-color: orange")
                self.input_devices_classes[inputs]._tab_widget.btn_on_off.setText('Off')
                self.input_devices_classes[inputs]._toggle_on_off(False)

        try:
            self.state_machine.request_state_change(State.IDLE)
            if len(self.input_devices_classes) != 0:
                self.state_machine.request_state_change(State.READY)
        except RuntimeError:
            return False
        return super().stop()

    def load_settings_from_file(self, settings_file_path):

        self.state_machine.request_state_change(State.IDLE)

        if self.state_machine.current_state == State.IDLE:
            self.settings.load_from_file(settings_file_path)
            self.share_settings(self.settings)

    def prepare_load_settings(self):
        """
        Prepare the module for new settings: remove all 'old' hardware from the list
        :return:
        """
        # remove_input_device any existing input devices
        for key in list(self.input_devices_classes.keys()):
            self.remove_input_device(key)

    def apply_loaded_settings(self):
        """
        Create hardware inputs based on the loaded settings
        :return:
        """
        for keyboard_settings in self.settings.key_boards:
            self.add_a_keyboard(keyboard_settings=keyboard_settings)

        for joystick_settings in self.settings.joy_sticks:
            self.add_a_joystick(joystick_settings=joystick_settings)

        for sensodrive_settings in self.settings.sensodrives:
            self.add_a_sensodrive(sensodrive_settings=sensodrive_settings)

    def add_a_keyboard(self, keyboard_settings=None):
        """
        Adds a keyboard input
        :param keyboard_settings: self-explanatory
        :return:
        """
        number_of_keyboards = sum([bool("Keyboard" in k) for k in self.input_devices_classes.keys()])
        device_name = "Keyboard %s" % (number_of_keyboards + 1)

        is_a_new_keyboard = not keyboard_settings
        if is_a_new_keyboard:
            keyboard_settings = KeyBoardSettings()
            keyboard_settings.name = device_name

        device = JOANKeyboard(self, keyboard_settings, name=device_name)
        self.module_dialog.add_device_tab(device)

        self.input_devices_classes.update({device_name: device})
        self.data[device_name] = device.process()
        self.write_news(self.data)

        if is_a_new_keyboard:
            self.settings.key_boards.append(keyboard_settings)

        return True

    def add_a_joystick(self, joystick_settings=None):
        """
        Adds a joystick input
        :param joystick_settings:
        :return:
        """
        number_of_joysticks = sum([bool("Joystick" in k) for k in self.input_devices_classes.keys()])
        device_name = "Joystick %s" % (number_of_joysticks + 1)

        is_a_new_joystick = not joystick_settings
        if is_a_new_joystick:
            joystick_settings = JoyStickSettings()
            joystick_settings.name = device_name

        device = JOANJoystick(self, joystick_settings, name=device_name)
        self.module_dialog.add_device_tab(device)

        self.input_devices_classes.update({device_name: device})
        self.data[device_name] = device.process()
        self.write_news(self.data)

        if is_a_new_joystick:
            self.settings.joy_sticks.append(joystick_settings)

        return True

    def add_a_sensodrive(self, sensodrive_settings=None):
        """
        Adds a sensodrive input
        :param sensodrive_settings:
        :return:
        """
        # This is a temporary fix so that we cannot add another sensodrive which will make pcan crash because we only have one PCAN usb interface dongle
        number_of_sensodrives = sum([bool("SensoDrive" in k) for k in self.input_devices_classes.keys()])

        if number_of_sensodrives < 2:
            device_name = "SensoDrive %s" % (number_of_sensodrives + 1)

            is_a_new_sensodrive = not sensodrive_settings
            if is_a_new_sensodrive:
                sensodrive_settings = SensoDriveSettings()
                sensodrive_settings.name = device_name

            device = JOANSensoDrive(self, number_of_sensodrives, sensodrive_settings, name=device_name)
            self.module_dialog.add_device_tab(device)

            self.input_devices_classes.update({device_name: device})
            self.data[device_name] = device.process()
            self.write_news(self.data)

            if is_a_new_sensodrive:
                self.settings.sensodrives.append(sensodrive_settings)
            return True
        else:
            return False

    def remove_input_device(self, device_name):
        """
        Removes an input
        :param device_name: name of the input
        :return:
        """
        if "Keyboard" in device_name:
            keyboard.unhook(self.input_devices_classes[device_name].key_event)

        # remove device from settings object
        self.settings.remove_input_device(device_name)

        # get rid of the device tab
        self.input_devices_classes[device_name].remove_tab()

        # delete the input device object
        del self.input_devices_classes[device_name]

        # remove device from data (news)
        try:
            del self.data[device_name]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        if not self.input_devices_classes:
            self.stop()
