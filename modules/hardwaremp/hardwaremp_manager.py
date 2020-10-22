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
        for idx, _ in enumerate(self.settings.key_boards):
            self.shared_values.keyboards.update({'Keyboard ' + str(idx): KeyboardSharedValues()})
        for idx, _ in enumerate(self.settings.joy_sticks):
            self.shared_values.joysticks.update({'Joystick ' + str(idx): JoystickSharedValues()})
        for idx, _ in enumerate(self.settings.sensodrives):
            self.shared_values.sensodrives.update({'SensoDrive ' + str(idx): SensoDriveSharedValues()})


    def add_hardware_input(self, hardware_input_type, hardware_input_name, hardware_input_settings=None):
        " Here we just add the settings and settings dialog functionality"
        if not hardware_input_settings:
            hardware_input_settings = hardware_input_type.settings
            if hardware_input_type == HardwareInputTypes.KEYBOARD:
                self.settings.key_boards.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.JOYSTICK:
                self.settings.joy_sticks.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.SENSODRIVE:
                self.settings.sensodrives.append(hardware_input_settings)

        self._hardware_input_settings_dict[hardware_input_name] = hardware_input_settings
        self._hardware_input_settingdialogs_dict[hardware_input_name] = hardware_input_type.klass_dialog(hardware_input_settings)

    def _open_settings_dialog(self, hardware_input_name):
        self._hardware_input_settingdialogs_dict[hardware_input_name].show()


    def _remove_hardware_input_device(self, hardware_input_name):
        # Remove settings if they are available
        self.settings.remove_hardware_input_device(self._hardware_input_settings_dict[hardware_input_name])

        # Remove settings dialog
        self._hardware_input_settingdialogs_dict[hardware_input_name].setParent(None)
        del self._hardware_input_settingdialogs_dict[hardware_input_name]


