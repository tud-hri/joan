from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from .hardwaremp_inputtypes import HardwareInputTypes
from .hardwaremp_settings import HardwareMPSettings
from .hardwaremp_sharedvalues import KeyboardSharedValues, JoystickSharedValues, SensoDriveSharedValues
from PyQt5 import uic


class HardwareMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, time_step_in_ms=time_step_in_ms, parent=parent)
        self._hardware_inputs = {}
        self.hardware_input_type = None
        self.hardware_input_settings = None

        self._hardware_input_settings_dict = {}
        self._hardware_input_tabs_dict = {}
        self._hardware_input_settingdialogs_dict = {}

        self.settings = HardwareMPSettings()

    def initialize(self):
        super().initialize()
        self.module_settings = self.settings
        total_amount_of_keyboards = len(self.settings.key_boards)
        total_amount_of_joysticks = len(self.settings.joy_sticks)
        total_amount_of_sensodrives = len(self.settings.sensodrives)

        for i in range(0, total_amount_of_keyboards):
            self.shared_values.keyboards.update({'Keyboard ' + str(i): KeyboardSharedValues()})

        for j in range(0, total_amount_of_joysticks):
            self.shared_values.joysticks.update({'Joystick ' + str(j): JoystickSharedValues()})

        for k in range(0, total_amount_of_sensodrives):
            self.shared_values.sensodrives.update({'SensoDrive ' + str(k): SensoDriveSharedValues()})

    def add_hardware_input(self, hardware_input_type, hardware_input_settings=None):
        number_of_inputs = sum([bool(hardware_input_type.__str__() in k) for k in self._hardware_input_tabs_dict.keys()]) + 1
        hardware_input_name = hardware_input_type.__str__() + ' ' + str(number_of_inputs)

        if not hardware_input_settings:
            hardware_input_settings = hardware_input_type.settings
            if hardware_input_type == HardwareInputTypes.KEYBOARD:
                self.settings.key_boards.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.JOYSTICK:
                self.settings.joy_sticks.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.SENSODRIVE:
                self.settings.sensodrives.append(hardware_input_settings)

        self._hardware_input_tabs_dict[hardware_input_name] = uic.loadUi(hardware_input_type.hardware_tab_ui_file)
        self._hardware_input_settings_dict[hardware_input_name] = hardware_input_settings
        self._hardware_input_settingdialogs_dict[hardware_input_name] = hardware_input_type.klass_dialog(hardware_input_settings)

        self._hardware_input_tabs_dict[hardware_input_name].groupBox.setTitle(hardware_input_name)

        self.module_dialog._module_widget.hardware_list_layout.addWidget(self._hardware_input_tabs_dict[hardware_input_name])
        self._hardware_input_tabs_dict[hardware_input_name].btn_settings.clicked.connect(lambda: self._open_settings_dialog(hardware_input_name))
        self._hardware_input_tabs_dict[hardware_input_name].btn_remove_hardware.clicked.connect(lambda: self._remove_hardware_input_device(hardware_input_name))

    def _remove_hardware_input_device(self, hardware_input_name):
        # Remove settings if they are available
        self.settings.remove_hardware_input_device(self._hardware_input_settings_dict[hardware_input_name])

        # Remove dialog
        self._hardware_input_tabs_dict[hardware_input_name].setParent(None)
        del self._hardware_input_tabs_dict[hardware_input_name]

        # Remove settings dialog
        self._hardware_input_settingdialogs_dict[hardware_input_name].setParent(None)
        del self._hardware_input_settingdialogs_dict[hardware_input_name]

    def _open_settings_dialog(self, hardware_input_name):
        self._hardware_input_settingdialogs_dict[hardware_input_name].show()


