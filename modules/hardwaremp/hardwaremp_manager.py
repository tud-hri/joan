
import os

from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from core.module_manager import ModuleManager
from .hardwaremp_inputtypes import HardwareInputTypes
from .hardwaremp_settings import HardwareManagerSettings
from core.statesenum import State


class HardwareMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step=1, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, time_step=time_step, parent=parent)
        self._hardware_inputs = {}
        self.settings = HardwareManagerSettings(module_enum=JOANModules.HARDWARE_MP)


    def initialize(self):
        return super().initialize()

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
            self._hardware_inputs[hardware_input_name].get_hardware_input_tab.groupBox.setTitle(hardware_input_name)
            self.module_dialog._module_widget.hardware_list_layout.addWidget(self._hardware_inputs[hardware_input_name].get_hardware_input_tab)

            self._hardware_inputs[hardware_input_name]._open_settings_dialog_from_button()

        else:
            self._hardware_inputs[hardware_input_name] = hardware_input_type.klass(self, hardware_input_name,
                                                                                   hardware_input_settings)
            self._hardware_inputs[hardware_input_name].get_hardware_input_tab.groupBox.setTitle(hardware_input_name)
            self.module_dialog.module_widget.hardware_list_layout.addWidget(
                self._hardware_inputs[hardware_input_name].get_hardware_input_tab)
            self._hardware_inputs[hardware_input_name]._open_settings_dialog()

        return self._hardware_inputs[hardware_input_name].get_hardware_input_tab

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

