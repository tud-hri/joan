from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from core.statesenum import State
from modules.joanmodules import JOANModules
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from PyQt5 import uic


import os


class HardwareMPDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, module_manager=module_manager, parent=parent)
        # Loading the inputtype dialog (in which we will be able to add hardwareclasses dynamically)
        self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "uis/inputtype.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.add_selected_hardware_input)

        #connect the add hardware button to showing our just created inputtype dialog
        self._module_widget.btn_add_hardware.clicked.connect(self._hardware_input_selection)

    def _handle_state_change(self):
        """
        We only want to be able to add hardware when we are in the stopped state, therefore we add this to the state change listener
        for this module. We should however not forget also calling the super()._handle_state_change() method.
        """
        super()._handle_state_change()
        if self._module_manager.state_machine.current_state != State.STOPPED:
            self._module_widget.btn_add_hardware.setEnabled(False)
            self._module_widget.hardware_groupbox.setEnabled(False)
        else:
            self._module_widget.btn_add_hardware.setEnabled(True)
            self._module_widget.hardware_groupbox.setEnabled(True)

    def _hardware_input_selection(self):
        self._input_type_dialog.combo_hardware_inputtype.clear()
        for hardware_inputs in HardwareInputTypes:
            self._input_type_dialog.combo_hardware_inputtype.addItem(hardware_inputs.__str__(),
                                                                             userData=hardware_inputs)
        self._input_type_dialog.show()

    def add_selected_hardware_input(self):
        chosen_hardware_input = self._input_type_dialog.combo_hardware_inputtype.itemData(self._input_type_dialog.combo_hardware_inputtype.currentIndex())
        #self._module_manager.add_hardware_input(chosen_hardware_input)
        self._module_manager.set_runtime_settings(**{str(chosen_hardware_input): self._input_type_dialog.combo_hardware_inputtype})



