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
from process.status import Status


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

        self.state_machine.add_state_change_listener(self._state_change_listener)

        default_settings_file_location = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                      'hardware_settings.json')
        if os.path.isfile(default_settings_file_location):
            self.settings.load_from_file(default_settings_file_location)

        self.share_settings(self.settings)

    def __del__(self):
        print("Destructor HardwareManager")

        # remove all hardware

        super(JoanModuleAction, self).__del__()

    def _state_change_listener(self):
        """
        Listens to any statechange of the module, whenever the state changes this will be executed.
        :return:
        """
        for inputs in self.input_devices_classes:
            self.data[inputs] = self.input_devices_classes[inputs].process()

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
        self.carla_interface_status = self.status.get_module_current_state(JOANModules.CARLA_INTERFACE)

        self.sw_controller_data = self.read_news(JOANModules.STEERING_WHEEL_CONTROL)

        for inputs in self.input_devices_classes:
            self.data[inputs] = self.input_devices_classes[inputs].process()
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
                            self.data[inputs] = self.input_devices_classes[inputs].process()
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
        #make sure you can only turn on the motor of the wheel if carla is connected
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
                self.input_devices_classes[inputs]._sensodrive_tab.btn_on_off.setStyleSheet("background-color: orange")
                self.input_devices_classes[inputs]._sensodrive_tab.btn_on_off.setText('Off')
                self.input_devices_classes[inputs]._toggle_on_off(False)

        try:
            self.state_machine.request_state_change(State.IDLE)
            if len(self.input_devices_classes) != 0:
                self.state_machine.request_state_change(State.READY)
        except RuntimeError:
            return False
        return super().stop()

    def load_settings(self, settings_file_to_load):
        self._load_settings_from_file(settings_file_to_load)
        self.initialize()

    def add_a_keyboard(self, widget, keyboard_settings=None):
        """
        Adds a keyboard input
        :param widget:
        :param keyboard_settings:
        :return:
        """
        is_a_new_keyboard = not keyboard_settings
        if is_a_new_keyboard:
            keyboard_settings = KeyBoardSettings()

        number_of_keyboards = sum([bool("Keyboard" in k) for k in self.input_devices_classes.keys()])
        device_title = "Keyboard %s" % (number_of_keyboards + 1)
        self.input_devices_classes.update([(device_title, JOANKeyboard(self, widget, keyboard_settings))])
        if is_a_new_keyboard:
            self.settings.key_boards.append(keyboard_settings)

        return device_title

    def add_a_joystick(self, widget, joystick_settings=None):
        """
        Adds a joystick input
        :param widget:
        :param joystick_settings:
        :return:
        """
        is_a_new_joystick = not joystick_settings
        if is_a_new_joystick:
            joystick_settings = JoyStickSettings()

        number_of_joysticks = sum([bool("Joystick" in k) for k in self.input_devices_classes.keys()])
        device_title = "Joystick %s" % (number_of_joysticks + 1)

        self.input_devices_classes.update([(device_title, JOANJoystick(self, widget, joystick_settings))])
        if is_a_new_joystick:
            self.settings.joy_sticks.append(joystick_settings)
        return device_title

    def add_a_sensodrive(self, widget, sensodrive_settings=None):
        """
        Adds a sensodrive input
        :param widget:
        :param sensodrive_settings:
        :return:
        """
        is_a_new_sensodrive = not sensodrive_settings
        if is_a_new_sensodrive:
            sensodrive_settings = SensoDriveSettings()

        ## This is a temporary fix so that we cannot add another sensodrive which will make pcan crash because we only have one PCAN usb interface dongle
        number_of_sensodrives = sum([bool("SensoDrive" in k) for k in self.input_devices_classes.keys()])

        if number_of_sensodrives < 2:
            device_title = "SensoDrive %s" % (number_of_sensodrives + 1)

            self.input_devices_classes.update([(device_title, JOANSensoDrive(self, widget, number_of_sensodrives, sensodrive_settings))])
            if is_a_new_sensodrive:
                self.settings.sensodrives.append(sensodrive_settings)
            return device_title
        else:
            return 'DO_NOT_ADD'

    def remove(self, tabtitle):
        """
        Removes an input
        :param tabtitle: name of the input
        :return:
        """
        if "Keyboard" in tabtitle:
            keyboard.unhook(self.input_devices_classes[tabtitle].key_event)

        del self.input_devices_classes[tabtitle]

        try:
            del self.data[tabtitle]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        if not self.input_devices_classes:
            self.stop()
