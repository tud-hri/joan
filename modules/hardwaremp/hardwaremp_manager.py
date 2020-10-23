from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from .hardwaremp_inputtypes import HardwareInputTypes
from .hardwaremp_sharedvalues import KeyboardSharedValues, JoystickSharedValues, SensoDriveSharedValues


class HardwareMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, time_step_in_ms=time_step_in_ms, parent=parent)
        self._hardware_inputs = {}
        self.hardware_input_type = None
        self.hardware_input_settings = None

        self._hardware_input_settings_dict = {}  # TODO: Wat is deze? Deze is nu nodig om de individuele settings bij te houden, maar is een extra lijst (dezelfde lijst zit ook al in self.module_settings. Wordt gebruikt in regel 52. Maar, we kunnen settings ook removen op input naam of identifier. Kan deze dict weg.
        self._hardware_input_settingdialogs_dict = {}

        self.settings = self.module_settings

    def initialize(self):
        super().initialize()
        self.module_settings = self.settings
        for keyboard in self.settings.key_boards:
            self.shared_values.keyboards['Keyboard' + str(keyboard.identifier)] = KeyboardSharedValues()
        for joystick in self.settings.joy_sticks:
            self.shared_values.joysticks['Joystick' + str(joystick.identifier)] = JoystickSharedValues()
        for sensodrive in self.settings.sensodrives:
            self.shared_values.sensodrives['SensoDrive' + str(sensodrive.identifier)] = SensoDriveSharedValues()


    def _add_hardware_input(self, hardware_input_type, hardware_input_settings = None):
        " Here we just add the settings and settings dialog functionality"
        if not hardware_input_settings:
            hardware_input_settings = hardware_input_type.settings()
            #Keyboard (make sure we have unique identifiers)
            if hardware_input_type == HardwareInputTypes.KEYBOARD:
                keyboard_amount = len(self.settings.key_boards)
                if keyboard_amount == 0:
                    self.settings.key_boards.append(hardware_input_settings)
                else:
                    for keyboard_settings in self.settings.key_boards:
                        if keyboard_settings.identifier == keyboard_amount:
                            keyboard_identifier = keyboard_settings.identifier + 1
                        else:
                            keyboard_identifier = keyboard_amount
                    hardware_input_settings = hardware_input_type.settings(keyboard_identifier)
                    self.settings.key_boards.append(hardware_input_settings)

            #Joystick
            if hardware_input_type == HardwareInputTypes.JOYSTICK:
                joystick_amount = len(self.settings.joy_sticks)
                if joystick_amount == 0:
                    self.settings.joy_sticks.append(hardware_input_settings)
                else:
                    for joystick_settings in self.settings.joy_sticks:
                        if joystick_settings.identifier == joystick_amount:
                            joystick_identifier = joystick_settings.identifier + 1
                        else:
                            joystick_identifier = joystick_amount
                    hardware_input_settings = hardware_input_type.settings(joystick_identifier)
                    self.settings.joy_sticks.append(hardware_input_settings)

            if hardware_input_type == HardwareInputTypes.SENSODRIVE:
                sensodrive_amount = len(self.settings.sensodrives)
                if sensodrive_amount == 0:
                    self.settings.sensodrives.append(hardware_input_settings)
                else:
                    for sensodrive_settings in self.settings.sensodrives:
                        if sensodrive_settings.identifier == sensodrive_amount:
                            sensodrive_identifier = sensodrive_settings.identifier + 1
                        else:
                            sensodrive_identifier = sensodrive_amount
                    hardware_input_settings = hardware_input_type.settings(sensodrive_identifier)
                    self.settings.sensodrives.append(hardware_input_settings)

        # self._hardware_input_settings_dict[hardware_input_name] = hardware_input_settings
        hardware_input_name = hardware_input_type.__str__() + str(hardware_input_settings.identifier)
        self._hardware_input_settingdialogs_dict[hardware_input_name] = hardware_input_type.klass_dialog(hardware_input_settings)
        return hardware_input_name

    def _open_settings_dialog(self, hardware_input_name):
        self._hardware_input_settingdialogs_dict[hardware_input_name].show()


    def _remove_hardware_input_device(self, hardware_input_name):
        # Remove settings if they are available
        if 'Keyboard' in hardware_input_name:
            identifier_str = hardware_input_name.replace('Keyboard', '')
            identifier = int(identifier_str)
            for keyboards in self.settings.key_boards:
                if keyboards.identifier == identifier:
                    settings_object = keyboards

        if 'Joystick' in hardware_input_name:
            identifier_str = hardware_input_name.replace('Joystick', '')
            identifier = int(identifier_str)
            for joysticks in self.settings.joy_sticks:
                if joysticks.identifier == identifier:
                    settings_object = joysticks

        if 'SensoDrive' in hardware_input_name:
            identifier_str = hardware_input_name.replace('SensoDrive', '')
            identifier = int(identifier_str)
            for sensodrives in self.settings.sensodrives:
                if sensodrives.identifier == identifier:
                    settings_object = sensodrives

        self.settings.remove_hardware_input_device(settings_object)

        # Remove settings dialog
        self._hardware_input_settingdialogs_dict[hardware_input_name].setParent(None)
        del self._hardware_input_settingdialogs_dict[hardware_input_name]


    def _turn_on(self, hardware_input_name):
        identifier_str = hardware_input_name.replace('SensoDrive', '')
        identifier = int(identifier_str)
        for sensodrives in self.settings.sensodrives:
            if sensodrives.identifier == identifier:
                settings_object = sensodrives

        settings_object.init_event.set()


