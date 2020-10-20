from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from .hardwaremp_inputtypes import HardwareInputTypes
from .hardwaremp_settings import HardwareMPSettings
from .hardwaremp_sharedvalues import KeyboardSharedValues


class HardwareMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, time_step_in_ms=time_step_in_ms, parent=parent)
        self._hardware_inputs = {}
        self.settings = HardwareMPSettings()

    def initialize(self):
        super().initialize()
        self.module_settings = self.settings
        total_amount_of_keyboards = len(self.settings.key_boards)
        for i in range(0, total_amount_of_keyboards):
            self.shared_values.keyboards.update({'Keyboard ' + str(i): KeyboardSharedValues()})

    def get_ready(self):
        return super().get_ready()

    def start(self):
        return super().start()

    def stop(self):
        return super().stop()

    def add_hardware_input(self, hardware_input_type, hardware_input_settings=None):
        number_of_inputs = sum([bool(hardware_input_type.__str__() in k) for k in self._hardware_inputs.keys()]) + 1
        hardware_input_name = hardware_input_type.__str__() + ' ' + str(number_of_inputs)

        if not hardware_input_settings:
            hardware_input_settings = hardware_input_type.settings
            if hardware_input_type == HardwareInputTypes.KEYBOARD:
                self.settings.key_boards.append(hardware_input_settings)

        self._hardware_inputs[hardware_input_name] = hardware_input_type.klass(self, hardware_input_name, hardware_input_settings)
        hardware_tab = self._hardware_inputs[hardware_input_name].get_hardware_input_tab
        hardware_tab.groupBox.setTitle(hardware_input_name)

        self.module_dialog._module_widget.hardware_list_layout.addWidget(hardware_tab)

        return hardware_tab

    def remove_hardware_input_device(self, hardware_input):
        try:
            self.settings.remove_hardware_input_device(
                self._hardware_inputs[hardware_input.get_hardware_input_list_key].settings)
        except ValueError:  # depends if right controller list is present
            pass

        # remove dialog
        self._hardware_inputs[hardware_input.get_hardware_input_list_key].get_hardware_input_tab.setParent(None)

        # delete object
        del self._hardware_inputs[hardware_input.get_hardware_input_list_key]
