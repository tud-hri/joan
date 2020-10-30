from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from .hardwaremp_inputtypes import HardwareInputTypes
from core.statesenum import State
import queue
import time


class HardwareMPManager(ModuleManager):
    """Hardwaremanager keeps track of which inputs are being used with what settings. """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, time_step_in_ms=time_step_in_ms, parent=parent)
        self._hardware_inputs = {}
        self.hardware_input_type = None
        self.hardware_input_settings = None

        self._hardware_input_settingdialogs_dict = {}



    def get_ready(self):
        if len(self.module_settings.sensodrives) != 0:
            self.module_dialog.update_timer.timeout.connect(self.module_dialog._update_sensodrive_state)
            self.module_dialog.update_timer.start()
        super().get_ready()

    def initialize(self):
        super().initialize()

        # create shared variables for all inputs in the settings
        for keyboard in self.module_settings.keyboards.values():
            self.shared_variables.keyboards[keyboard.identifier] = keyboard.input_type.shared_variables()
        for joystick in self.module_settings.joysticks.values():
            self.shared_variables.joysticks[joystick.identifier] = joystick.input_type.shared_variables()
        for sensodrive in self.module_settings.sensodrives.values():
            self.shared_variables.sensodrives[sensodrive.identifier] = sensodrive.input_type.shared_variables()

    def start(self):
        super().start()
        for sensodrives in self.module_settings.sensodrives.values():
            if sensodrives.current_state != 0x14:
                sensodrives.turn_on_event.set()

    def stop(self):
        for sensodrives in self.module_settings.sensodrives.values():
            sensodrives.turn_off_event.set()
            sensodrives.close_event.set()
        super().stop()

    def _add_hardware_input(self, input_type, input_settings=None):
        """
        Add hardware input
        :param input_type:
        :param input_settings:
        :return:
        """
        if not input_settings:
            input_settings = input_type.settings(input_type)

            # find unique identifier
            type_dict = None
            if input_type == HardwareInputTypes.KEYBOARD:
                type_dict = self.module_settings.keyboards
            elif input_type == HardwareInputTypes.JOYSTICK:
                type_dict = self.module_settings.joysticks
            elif input_type == HardwareInputTypes.SENSODRIVE:
                type_dict = self.module_settings.sensodrives

            identifier = 0
            for v in type_dict.values():
                if v.identifier > identifier:
                    identifier = v.identifier
            input_settings.identifier = identifier + 1

        # check if settings do not already exist
        if input_type == HardwareInputTypes.KEYBOARD:
            if input_settings not in self.module_settings.keyboards.values():
                self.module_settings.keyboards[input_settings.identifier] = input_settings
        elif input_type == HardwareInputTypes.JOYSTICK:
            if input_settings not in self.module_settings.joysticks.values():
                self.module_settings.joysticks[input_settings.identifier] = input_settings
        elif input_type == HardwareInputTypes.SENSODRIVE:
            if input_settings not in self.module_settings.sensodrives.values():
                self.module_settings.sensodrives[input_settings.identifier] = input_settings

        # create dialog thing
        input_name = '{0!s} {1!s}'.format(input_type, str(input_settings.identifier))
        self._hardware_input_settingdialogs_dict[input_name] = input_type.klass_dialog(input_settings)
        return input_name, input_settings.identifier

    def _open_settings_dialog(self, input_name):
        self._hardware_input_settingdialogs_dict[input_name].show()

    def _remove_hardware_input_device(self, input_name):

        # Remove settings if they are available
        settings_object = None
        #TODO Check if we can do this with the identifier only instead of the string mess
        if 'Keyboard' in input_name:
            identifier = int(input_name.replace('Keyboard', ''))
            for keyboard in self.module_settings.keyboards.values():
                if keyboard.identifier == identifier:
                    settings_object = keyboard

        if 'Joystick' in input_name:
            identifier = int(input_name.replace('Joystick', ''))
            for joystick in self.module_settings.joysticks.values():
                if joystick.identifier == identifier:
                    settings_object = joystick

        if 'SensoDrive' in input_name:
            identifier = int(input_name.replace('SensoDrive', ''))
            for sensodrive in self.module_settings.sensodrives.values():
                if sensodrive.identifier == identifier:
                    settings_object = sensodrive

        self.module_settings.remove_hardware_input_device(settings_object)

        # Remove settings dialog
        self._hardware_input_settingdialogs_dict[input_name].setParent(None)
        del self._hardware_input_settingdialogs_dict[input_name]

    def _turn_on(self, identifier):
        self.module_settings.sensodrives[identifier].turn_on_event.set()

    def _turn_off(self, identifier):
        self.module_settings.sensodrives[identifier].turn_off_event.set()

    def _clear_error(self, identifier):
        self.module_settings.sensodrives[identifier].clear_error_event.set()
