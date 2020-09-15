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
        for hardware_input in self._hardware_inputs:
            self.data[hardware_input] = self._hardware_inputs[hardware_input].do()

        for hardware_input in self._hardware_inputs:
            if self.state_machine.current_state == State.READY or self.state_machine.current_state == State.IDLE:
                self._hardware_inputs[hardware_input].enable_remove_button()
            else:
                self._hardware_inputs[hardware_input].disable_remove_button()
        self.write_news(self.data)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        self.carla_interface_data = self.read_news(JOANModules.CARLA_INTERFACE)
        self.carla_interface_status = self.singleton_status.get_module_current_state(JOANModules.CARLA_INTERFACE)

        self.sw_controller_data = self.read_news(JOANModules.STEERING_WHEEL_CONTROL)

        for hardware_input in self._hardware_inputs:
            self.data[hardware_input] = self._hardware_inputs[hardware_input].do()
            if hardware_input == HardwareInputTypes.SENSODRIVE:
                 self._hardware_inputs[hardware_input]._toggle_on_off(self.carla_interface_data['connected'])

        self.write_news(self.data)

    def initialize(self):
        """
        This function is called before the module is started and will try to initialize any added hardware inputs
        """
        try:
            if self.state_machine.current_state == State.IDLE:
                if len(self._hardware_inputs) != 0:
                    for input_device in self._hardware_inputs:
                        self._hardware_inputs[input_device].initialize()
                        self.state_machine.request_state_change(State.READY, '')
                        for inputs in self._hardware_inputs:
                            self.data[inputs] = self._hardware_inputs[inputs].do()
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
        for hardware_input in self._hardware_inputs:
            if hardware_input == HardwareInputTypes.SENSODRIVE:
                self._hardware_inputs[hardware_input]._toggle_on_off(self.carla_interface_data['connected'])

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
                 self._hardware_inputs[hardware_input]._hardware_input_tab.btn_on_off.setStyleSheet("background-color: orange")
                 self._hardware_inputs[hardware_input]._hardware_input_tab.btn_on_off.setText('Off')
                 self._hardware_inputs[hardware_input]._toggle_on_off(False)

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
        for device in self._hardware_inputs:
            self.remove_hardware_input_device(device)

    def apply_loaded_settings(self):
        """
        Create hardware inputs based on the loaded settings
        :return:
        """
        for keyboard_settings in self.settings.key_boards:
            self.add_hardware_input(HardwareInputTypes.KEYBOARD, keyboard_settings)

        for joystick_settings in self.settings.joy_sticks:
            self.add_hardware_input(HardwareInputTypes.JOYSTICK, joystick_settings)

        for sensodrive_settings in self.settings.sensodrives:
            self.add_hardware_input(HardwareInputTypes.SENSODRIVE, sensodrive_settings)



    def add_hardware_input(self, hardware_input_type, hardware_input_settings = None):
        number_of_inputs = sum([bool(hardware_input_type.__str__() in k) for k in self._hardware_inputs.keys()]) + 1
        hardware_input_name = hardware_input_type.__str__() + ' ' + str(number_of_inputs)

        if not hardware_input_settings:
            hardware_input_settings = hardware_input_type.settings
            if hardware_input_type == HardwareInputTypes.KEYBOARD:
                self.settings.key_boards.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.JOYSTICK:
                self.settings.joy_sticks.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.SENSODRIVE:
                self.settings.sensodrives.append(hardware_input_settings)

            self._hardware_inputs[hardware_input_name] = hardware_input_type.klass(self, hardware_input_name, hardware_input_settings)
            self._hardware_inputs[hardware_input_name].get_hardware_input_tab.groupBox.setTitle(hardware_input_name)
            self.module_dialog.module_widget.hardware_list_layout.addWidget(self._hardware_inputs[hardware_input_name].get_hardware_input_tab)

            self._hardware_inputs[hardware_input_name]._open_settings_dialog_from_button()

        else:
            self._hardware_inputs[hardware_input_name] = hardware_input_type.klass(self, hardware_input_name,
                                                                                   hardware_input_settings)
            self._hardware_inputs[hardware_input_name].get_hardware_input_tab.groupBox.setTitle(hardware_input_name)
            self.module_dialog.module_widget.hardware_list_layout.addWidget(
                self._hardware_inputs[hardware_input_name].get_hardware_input_tab)
            self._hardware_inputs[hardware_input_name]._open_settings_dialog()

        self._state_change_listener()

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
