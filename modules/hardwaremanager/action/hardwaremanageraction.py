import os

import keyboard

from modules.hardwaremanager.action.hardwaremanagersettings import HardwareManagerSettings
from modules.hardwaremanager.action.hwinputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules
from core.joanmoduleaction import JoanModuleAction
from core.statesenum import State


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
        self.data = {}
        self.write_news(news=self.data)
        self._hardware_inputs = {}

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
        pass
        # for inputs in self.input_devices_classes:
        #     self.data[inputs] = self.input_devices_classes[inputs].do()
        #
        # for inputs in self.input_devices_classes:
        #     if self.state_machine.current_state == State.READY or self.state_machine.current_state == State.IDLE:
        #         self.input_devices_classes[inputs].enable_remove_button()
        #     else:
        #         self.input_devices_classes[inputs].disable_remove_button()
        # self.write_news(self.data)

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
        for hardware_input in self.hardware_inputs:
            if hardware_input == HardwareInputTypes.SENSODRIVE:
                pass
            # if 'SensoDrive' in hardware_inputs.:
            #     self.input_devices_classes[inputs]._tab_widget.btn_on_off.setStyleSheet("background-color: orange")
            #     self.input_devices_classes[inputs]._tab_widget.btn_on_off.setText('Off')
            #     self.input_devices_classes[inputs]._toggle_on_off(False)

        try:
            self.state_machine.request_state_change(State.IDLE)
            if len(self._hardware_inputs) != 0:
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
            self.add_an_input(HardwareInputTypes.KEYBOARD, keyboard_settings)

        for joystick_settings in self.settings.joy_sticks:
            self.add_an_input(HardwareInputTypes.JOYSTICK, joystick_settings)

        for sensodrive_settings in self.settings.sensodrives:
            self.add_an_input(HardwareInputTypes.SENSODRIVE, sensodrive_settings)



    def add_hardware_input(self, hardware_input_type, hardware_input_settings = None):
        if not hardware_input_settings:
            hardware_input_settings = hardware_input_type.settings
            if hardware_input_type == HardwareInputTypes.KEYBOARD:
                self.settings.key_boards.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.JOYSTICK:
                self.settings.joy_sticks.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.SENSODRIVE:
                self.settings.sensodrives.append(hardware_input_settings)

        number_of_inputs = sum([bool(hardware_input_type.__str__() in k) for k in self._hardware_inputs.keys()]) + 1
        hardware_input_name = hardware_input_type.__str__() + ' ' + str(number_of_inputs)

        self._hardware_inputs[hardware_input_name] = hardware_input_type.klass(self, hardware_input_name, hardware_input_settings)
        self._hardware_inputs[hardware_input_name].get_hardware_input_tab.groupBox.setTitle(hardware_input_name)

        self.module_dialog.module_widget.hardware_list_layout.addWidget(self._hardware_inputs[hardware_input_name].get_hardware_input_tab)

        self._state_change_listener()

        if not hardware_input_settings:
            self._hardware_inputs[hardware_input_name]._open_settings_dialog_from_button()
        else:
            self._hardware_inputs[hardware_input_name]._open_settings_dialog()

        return self._hardware_inputs[hardware_input_name].get_hardware_input_tab

    def remove_hardware_input_device(self, hardware_input):
        # remove_input_device controller from the news
        try:
            del self.data[hardware_input.get_hardware_input_list_key]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        # remove_input_device controller settings
        try:
            self.settings.remove_hardware_input_device(
                self._hardware_inputs[hardware_input.get_hardware_input_list_key].settings)
        except ValueError:  # depends if right controller list is present
            pass

        try:
            self.settings.remove_hardware_input_device(
                self._hardware_inputs[hardware_input.get_hardware_input_list_key].settings)
        except ValueError:  # depends if right controller list is present
            pass

        # remove dialog
        self._hardware_inputs[hardware_input.get_hardware_input_list_key].get_hardware_input_tab.setParent(None)

        # delete object
        del self._hardware_inputs[hardware_input.get_hardware_input_list_key]

        # remove controller from data
        try:
            del self.data[hardware_input]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        if not self._hardware_inputs:
            self.stop()

    @property
    def hardware_inputs(self):
        return self._hardware_inputs

    @property
    def current_hardware_input(self):
        return self._current_hardware_input

    # def add_a_keyboard(self, keyboard_settings=None):
    #     """
    #     Adds a keyboard input
    #     :param keyboard_settings: self-explanatory
    #     :return:
    #     """
    #     number_of_keyboards = sum([bool("Keyboard" in k) for k in self.input_devices_classes.keys()])
    #     device_name = "Keyboard %s" % (number_of_keyboards + 1)
    #
    #     is_a_new_keyboard = not keyboard_settings
    #     if is_a_new_keyboard:
    #         keyboard_settings = KeyBoardSettings()
    #         keyboard_settings.name = device_name
    #
    #     device = JOANKeyboard(self, keyboard_settings, name=device_name)
    #     self.module_dialog.add_device_tab(device)
    #
    #     self.input_devices_classes.update({device_name: device})
    #     self.data[device_name] = device.do()
    #     self.write_news(self.data)
    #
    #     if is_a_new_keyboard:
    #         self.settings.key_boards.append(keyboard_settings)
    #
    #     return True
    #
    # def add_a_joystick(self, joystick_settings=None):
    #     """
    #     Adds a joystick input
    #     :param joystick_settings:
    #     :return:
    #     """
    #     number_of_joysticks = sum([bool("Joystick" in k) for k in self.input_devices_classes.keys()])
    #     device_name = "Joystick %s" % (number_of_joysticks + 1)
    #
    #     is_a_new_joystick = not joystick_settings
    #     if is_a_new_joystick:
    #         joystick_settings = JoyStickSettings()
    #         joystick_settings.name = device_name
    #
    #     device = JOANJoystick(self, joystick_settings, name=device_name)
    #     self.module_dialog.add_device_tab(device)
    #
    #     self.input_devices_classes.update({device_name: device})
    #     self.data[device_name] = device.do()
    #     self.write_news(self.data)
    #
    #     if is_a_new_joystick:
    #         self.settings.joy_sticks.append(joystick_settings)
    #
    #     return True
    #
    # def add_a_sensodrive(self, sensodrive_settings=None):
    #     """
    #     Adds a sensodrive input
    #     :param sensodrive_settings:
    #     :return:
    #     """
    #     # This is a temporary fix so that we cannot add another sensodrive which will make pcan crash because we only have one PCAN usb interface dongle
    #     number_of_sensodrives = sum([bool("SensoDrive" in k) for k in self.input_devices_classes.keys()])
    #
    #     if number_of_sensodrives < 2:
    #         device_name = "SensoDrive %s" % (number_of_sensodrives + 1)
    #
    #         is_a_new_sensodrive = not sensodrive_settings
    #         if is_a_new_sensodrive:
    #             sensodrive_settings = SensoDriveSettings()
    #             sensodrive_settings.name = device_name
    #
    #         device = JOANSensoDrive(self, number_of_sensodrives, sensodrive_settings, name=device_name)
    #         self.module_dialog.add_device_tab(device)
    #
    #         self.input_devices_classes.update({device_name: device})
    #         self.data[device_name] = device.do()
    #         self.write_news(self.data)
    #
    #         if is_a_new_sensodrive:
    #             self.settings.sensodrives.append(sensodrive_settings)
    #         return True
    #     else:
    #         return False

    # def remove_input_device(self, device_name):
    #     """
    #     Removes an input
    #     :param device_name: name of the input
    #     :return:
    #     """
    #     if "Keyboard" in device_name:
    #         keyboard.unhook(self.input_devices_classes[device_name].key_event)
    #
    #     # remove device from settings object
    #     self.settings.remove_input_device(device_name)
    #
    #     # get rid of the device tab
    #     self.input_devices_classes[device_name].remove_tab()
    #
    #     # delete the input device object
    #     del self.input_devices_classes[device_name]
    #
    #     # remove device from data (news)
    #     try:
    #         del self.data[device_name]
    #     except KeyError:  # data is only present if the hardware manager ran since the hardware was added
    #         pass
    #
    #     if not self.input_devices_classes:
    #         self.stop()


