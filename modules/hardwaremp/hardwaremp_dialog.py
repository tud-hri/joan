import os

from PyQt5 import uic

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from core.statesenum import State
from modules.joanmodules import JOANModules
from .hardwaremp_inputtypes import HardwareInputTypes
import queue

class HardwareMPDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, module_manager=module_manager, parent=parent)

        # Loading the inputtype dialog (in which we will be able to add hardwareclasses dynamically)
        self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "inputtype.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.add_selected_hardware_input)

        # Connect the add hardware button to showing our just created inputtype dialog
        self._module_widget.btn_add_hardware.clicked.connect(self._hardware_input_selection)
        self._hardware_input_tabs_dict = {}

    def _handle_state_change(self):
        """
        We only want to be able to add hardware when we are in the stopped state, therefore we add this to the state change listener
        for this module. We should however not forget also calling the super()._handle_state_change() method.
        """
        super()._handle_state_change()
        #joysticks and keyboards
        if self.module_manager.state_machine.current_state != State.STOPPED:
            self._module_widget.btn_add_hardware.setEnabled(False)
            for hardware_tabs in self._hardware_input_tabs_dict:
                self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.setEnabled(False)
                self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.blockSignals(True)
                if 'SensoDrive' not in hardware_tabs:
                    self._hardware_input_tabs_dict[hardware_tabs].setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tabs].blockSignals(True)
            # self._module_widget.hardware_groupbox.setEnabled(False)
        else:
            self._module_widget.btn_add_hardware.setEnabled(True)
            for hardware_tabs in self._hardware_input_tabs_dict:
                self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.setEnabled(True)
                self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.blockSignals(False)
                if 'SensoDrive' not in hardware_tabs:
                    self._hardware_input_tabs_dict[hardware_tabs].setEnabled(True)
                    self._hardware_input_tabs_dict[hardware_tabs].blockSignals(False)

        #sensodrive specific
        if self.module_manager.state_machine.current_state == State.READY or self.module_manager.state_machine.current_state == State.RUNNING:
            for hardware_tabs in self._hardware_input_tabs_dict:
                if 'SensoDrive' in hardware_tabs:
                    self._hardware_input_tabs_dict[hardware_tabs].btn_on.setEnabled(True)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_on.blockSignals(False)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_off.setEnabled(True)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_off.blockSignals(False)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.setEnabled(True)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.blockSignals(False)
        else:
            for hardware_tabs in self._hardware_input_tabs_dict:
                if 'SensoDrive' in hardware_tabs:
                    self._hardware_input_tabs_dict[hardware_tabs].btn_on.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_on.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_off.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_off.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tabs].lbl_sensodrive_state.setStyleSheet("background-color: orange")
                    self._hardware_input_tabs_dict[hardware_tabs].lbl_sensodrive_state.setText('Off')



    def _update_sensodrive_state(self):
        for sensodrives in self.module_manager.module_settings.sensodrives.values():
            try:
                sensodrives.current_state = sensodrives.state_queue.get(timeout = 0)
            except queue.Empty:
                pass
            hardware_tab_identifier = str("SensoDrive " + str(sensodrives.identifier))
            if self.module_manager.state_machine.current_state == State.READY or self.module_manager.state_machine.current_state == State.RUNNING:
                if sensodrives.current_state == 0x10:
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_on.setEnabled(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_on.blockSignals(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_off.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_off.setStyleSheet(None)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_off.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_clear_error.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_clear_error.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_clear_error.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].lbl_sensodrive_state.setStyleSheet("background-color: orange")
                    self._hardware_input_tabs_dict[hardware_tab_identifier].lbl_sensodrive_state.setText('Off')
                elif sensodrives.current_state == 0x14:
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_on.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_on.setStyleSheet(None)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_on.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_off.setEnabled(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_off.blockSignals(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_clear_error.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_clear_error.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].lbl_sensodrive_state.setStyleSheet("background-color: lightgreen")
                    self._hardware_input_tabs_dict[hardware_tab_identifier].lbl_sensodrive_state.setText('On')
                elif sensodrives.current_state == 0x18:
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_on.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_on.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_off.setEnabled(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_off.blockSignals(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_clear_error.setEnabled(True)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].btn_clear_error.blockSignals(False)
                    self._hardware_input_tabs_dict[hardware_tab_identifier].lbl_sensodrive_state.setStyleSheet("background-color: red")
                    self._hardware_input_tabs_dict[hardware_tab_identifier].lbl_sensodrive_state.setText('Error')

    def _hardware_input_selection(self):
        self._input_type_dialog.combo_hardware_inputtype.clear()
        for hardware_inputs in HardwareInputTypes:
            self._input_type_dialog.combo_hardware_inputtype.addItem(hardware_inputs.__str__(), userData=hardware_inputs)
        self._input_type_dialog.show()

    def add_selected_hardware_input(self):
        " Here we add the hardware input tabs "
        # First we create the settings in the module manager (this will include an identifier which is used in the hardware name)
        chosen_hardware_input = self._input_type_dialog.combo_hardware_inputtype.itemData(self._input_type_dialog.combo_hardware_inputtype.currentIndex())
        hardware_input_name = self.module_manager._add_hardware_input(chosen_hardware_input)

        # Adding tab
        self._hardware_input_tabs_dict[hardware_input_name] = uic.loadUi(chosen_hardware_input.hardware_tab_ui_file)
        self._hardware_input_tabs_dict[hardware_input_name].groupBox.setTitle(hardware_input_name)
        self._module_widget.hardware_list_layout.addWidget(self._hardware_input_tabs_dict[hardware_input_name])

        # Connecting buttons
        self._hardware_input_tabs_dict[hardware_input_name].btn_settings.clicked.connect(
            lambda: self.module_manager._open_settings_dialog(hardware_input_name))
        self._hardware_input_tabs_dict[hardware_input_name].btn_remove_hardware.clicked.connect(lambda: self._remove_hardware_input_device(hardware_input_name))

        if 'SensoDrive' in hardware_input_name:
            self._hardware_input_tabs_dict[hardware_input_name].btn_on.clicked.connect(lambda: self.module_manager._turn_on(hardware_input_name))
            self._hardware_input_tabs_dict[hardware_input_name].btn_off.clicked.connect(lambda: self.module_manager._turn_off(hardware_input_name))
            self._hardware_input_tabs_dict[hardware_input_name].btn_clear_error.clicked.connect(lambda: self.module_manager._clear_error(hardware_input_name))

    def _remove_hardware_input_device(self, hardware_input_name):
        # Remove dialog
        self._hardware_input_tabs_dict[hardware_input_name].setParent(None)
        del self._hardware_input_tabs_dict[hardware_input_name]

        # We remove the settings dialog and settings object in the module_manager class
        self.module_manager._remove_hardware_input_device(hardware_input_name)
