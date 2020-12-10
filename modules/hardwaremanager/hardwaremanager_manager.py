from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from .hardwaremanager_inputtypes import HardwareInputTypes
import multiprocessing as mp
from core.statesenum import State


class SensoDriveEvents:
    """
    Class containing all events for communication between hardwaremanager and sensodrive
    """

    def __init__(self):
        # events
        self.turn_on_event = mp.Event()
        self.turn_off_event = mp.Event()
        self.clear_error_event = mp.Event()
        self.close_event = mp.Event()
        self.state_queue = mp.Queue()


class HardwareManager(ModuleManager):
    """Hardwaremanager keeps track of which inputs are being used with what settings. """

    def __init__(self, news, central_settings, signals, central_state_monitor, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MANAGER, news=news, central_settings=central_settings,
                         signals=signals, central_state_monitor=central_state_monitor, time_step_in_ms=time_step_in_ms, parent=parent)
        self._hardware_inputs = {}
        self.hardware_input_type = None
        self.hardware_input_settings = None

    def initialize(self):
        """
        Initializes the manager, executes when transitioning from the Stopped State.
        :return:
        """
        super().initialize()
        for hw_input in self.module_settings.inputs.values():
            self.shared_variables.inputs[hw_input.identifier] = HardwareInputTypes(hw_input.input_type).shared_variables()
            if hw_input.input_type == HardwareInputTypes.SENSODRIVE.value:
                hw_input.events = SensoDriveEvents()

    def get_ready(self):
        """
        Gets the module manager ready, executes after transitioning from the Initialized State. Will start the periodic
        timer that also checks the state of a sensodrive (if there are any)
        :return:
        """
        for inputs in self.module_settings.inputs.values():
            if inputs.input_type == HardwareInputTypes.SENSODRIVE.value:
                self.module_dialog.update_timer.timeout.connect(self.module_dialog.update_sensodrive_state)
                self.module_dialog.update_timer.start()
        super().get_ready()

        for inputs in self.module_settings.inputs.values():
            if inputs.input_type == HardwareInputTypes.SENSODRIVE.value:
                inputs.events.clear_error_event.set()

    def start(self):
        """
        Starts the module, executes after transitioning from the ready state. Will also turn on the sensodrive if
        there are any.
        :return:
        """
        super().start()
        for inputs in self.module_settings.inputs.values():
            if inputs.input_type == HardwareInputTypes.SENSODRIVE.value:
                if inputs.current_state != 0x14:
                    inputs.events.turn_on_event.set()

    def stop(self):
        """
         Stops the module, executes after transitioning from the ready state. Will also turn off the sensodrive if
         there are any.
         :return:
         """
        for inputs in self.module_settings.inputs.values():
            if inputs.input_type == HardwareInputTypes.SENSODRIVE.value:
                inputs.events.turn_off_event.set()
                inputs.events.close_event.set()
                del inputs.events
        super().stop()

    def load_from_file(self, settings_file_to_load):
        """
        Loads Settings from json file
        :param settings_file_to_load:
        :return:
        """
        # remove all settings from the dialog
        for hardware_input in self.module_settings.all_inputs().values():
            self.remove_hardware_input(hardware_input.identifier)

        # load settings from file into module_settings object
        self.module_settings.load_from_file(settings_file_to_load)

        # add all settings tp module_dialog
        from_button = False
        for hardware_input_settings in self.module_settings.all_inputs().values():
            self.add_hardware_input(HardwareInputTypes(hardware_input_settings.input_type), from_button,
                                    hardware_input_settings)

    def add_hardware_input(self, input_type: HardwareInputTypes, from_button, input_settings=None):
        """
        Adds the chosen hardware input, will create the settings object for it.
        :param input_type:
        :param from_button:
        :param input_settings:
        :return:
        """
        # add to module_settings
        input_settings = self.module_settings.add_hardware_input(input_type, input_settings)

        # add to module_dialog
        self.module_dialog.add_hardware_input(input_settings, from_button)

    def remove_hardware_input(self, identifier):
        """
        Removes the hardware input and the settings for it.
        :param identifier:
        :return:
        """
        # remove from settings
        self.module_settings.remove_hardware_input(identifier)

        # remove settings from dialog
        self.module_dialog.remove_hardware_input(identifier)

    def turn_on_sensodrive(self, identifier):
        """
        Toggles the event for turning on a sensodrive
        :param identifier:
        :return:
        """
        self.module_settings.inputs[identifier].events.turn_on_event.set()

    def turn_off_sensodrive(self, identifier):
        """
        Toggles the event for turning off a sensodrive
        :param identifier:
        :return:
        """
        self.module_settings.inputs[identifier].events.turn_off_event.set()

    def clear_error_sensodrive(self, identifier):
        """
        Toggles the event for clearing the error state of a sensodrive
        :param identifier:
        :return:
        """
        self.module_settings.inputs[identifier].events.clear_error_event.set()
