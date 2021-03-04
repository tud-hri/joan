import os
import queue

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMessageBox

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from core.statesenum import State
from modules.joanmodules import JOANModules

msg_box = QMessageBox()
msg_box.setTextFormat(QtCore.Qt.RichText)


class HardwareManagerDialog(ModuleDialog):
    """
    Dialog of the Hardware Manager Class, will handle all button presses and UI functionality.
    """
    pass
    # TODO: implement this, see hardwaremanager example below

    # def __init__(self, module_manager: ModuleManager, parent=None):
    #     """
    #     Initializes the class
    #     :param module_manager:
    #     :param parent:
    #     """
    #     super().__init__(module=JOANModules.HARDWARE_MANAGER, module_manager=module_manager, parent=parent)
    #
    #     # Loading the inputtype dialog (in which we will be able to add hardwareclasses dynamically)
    #     self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "select_input_type.ui"))
    #     self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self._hardware_input_selected)
    #
    #     # Connect the add hardware button to showing our just created inputtype dialog
    #     self.module_widget.btn_add_hardware.clicked.connect(self._select_hardware_input_type)
    #     self._hardware_input_tabs_dict = {}
    #     self._hardware_input_dialogs_dict = {}
    #
    # def update_dialog(self):
    #     """
    #     Updates the Dialog, this function is called at a rate of 10Hz.
    #     :return:
    #     """
    #     difference_dict = {k: self._hardware_input_tabs_dict[k] for k in set(self._hardware_input_tabs_dict) - set(self.module_manager.module_settings.inputs)}
    #     for key in difference_dict:
    #         self.remove_hardware_input(key)
    #
    #     for input_settings in self.module_manager.module_settings.inputs:
    #         if self.module_manager.module_settings.inputs[input_settings].identifier not in \
    #                 self._hardware_input_tabs_dict:
    #             self.add_hardware_input(self.module_manager.module_settings.inputs[input_settings], False)
    #         self._hardware_input_dialogs_dict[
    #             self.module_manager.module_settings.inputs[input_settings].identifier].display_values(
    #             self.module_manager.module_settings.inputs[input_settings])
    #
    # def _handle_state_change(self):
    #     """
    #     We only want to be able to add hardware when we are in the stopped state, therefore we add this to the state
    #     change listener for this module. We should however not forget also calling the super()._handle_state_change()
    #     method.
    #     """
    #     super()._handle_state_change()
    #
    #     state = self.module_manager.state_machine.current_state
    #
    #     # joysticks and keyboards
    #     if state != State.STOPPED:
    #         self.module_widget.btn_add_hardware.setEnabled(False)
    #         for hardware_tabs in self._hardware_input_tabs_dict:
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.setEnabled(False)
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.blockSignals(True)
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_settings.setEnabled(False)
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_settings.blockSignals(True)
    #             if str(HardwareInputTypes.SENSODRIVE) not in hardware_tabs:
    #                 self._hardware_input_tabs_dict[hardware_tabs].setEnabled(False)
    #                 self._hardware_input_tabs_dict[hardware_tabs].blockSignals(True)
    #     else:
    #         self.module_widget.btn_add_hardware.setEnabled(True)
    #         for hardware_tabs in self._hardware_input_tabs_dict:
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.setEnabled(True)
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_remove_hardware.blockSignals(False)
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_settings.setEnabled(True)
    #             self._hardware_input_tabs_dict[hardware_tabs].btn_settings.blockSignals(False)
    #             if str(HardwareInputTypes.SENSODRIVE) not in hardware_tabs:
    #                 self._hardware_input_tabs_dict[hardware_tabs].setEnabled(True)
    #                 self._hardware_input_tabs_dict[hardware_tabs].blockSignals(False)
    #
    #     # sensodrive specific
    #     if state == State.READY or state == State.RUNNING:
    #         for hardware_tabs in self._hardware_input_tabs_dict:
    #             if str(HardwareInputTypes.SENSODRIVE) in hardware_tabs:
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_on.setEnabled(True)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_on.blockSignals(False)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_off.setEnabled(True)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_off.blockSignals(False)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.setEnabled(True)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.blockSignals(False)
    #     else:
    #         for hardware_tabs in self._hardware_input_tabs_dict:
    #             if str(HardwareInputTypes.SENSODRIVE) in hardware_tabs:
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_on.setEnabled(False)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_on.blockSignals(True)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_off.setEnabled(False)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_off.blockSignals(True)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.setEnabled(False)
    #                 self._hardware_input_tabs_dict[hardware_tabs].btn_clear_error.blockSignals(True)
    #                 self._hardware_input_tabs_dict[hardware_tabs].lbl_sensodrive_state.setStyleSheet(
    #                     "background-color: orange")
    #                 self._hardware_input_tabs_dict[hardware_tabs].lbl_sensodrive_state.setText('Off')
    #
    # def update_sensodrive_state(self):
    #     """
    #     Updates the state label of a SensoDrive in the Tab. This goes via the MultiProcessing Queue class.
    #     :return:
    #     """
    #     for inputs in self.module_manager.module_settings.inputs.values():
    #         if inputs.input_type == HardwareInputTypes.SENSODRIVE.value:
    #             try:
    #                 inputs.current_state = inputs.events.state_queue.get(timeout=0)
    #             except queue.Empty:
    #                 pass
    #
    #             state = self.module_manager.state_machine.current_state
    #             tab_sensodrive = self._hardware_input_tabs_dict[inputs.identifier]
    #
    #             if state == State.READY or state == State.RUNNING:
    #                 if inputs.current_state == 0x10:
    #                     tab_sensodrive.btn_on.setEnabled(True)
    #                     tab_sensodrive.btn_on.blockSignals(False)
    #                     tab_sensodrive.btn_off.setEnabled(False)
    #                     tab_sensodrive.btn_off.setStyleSheet(None)
    #                     tab_sensodrive.btn_off.blockSignals(True)
    #                     tab_sensodrive.btn_clear_error.setEnabled(False)
    #                     tab_sensodrive.btn_clear_error.blockSignals(True)
    #                     tab_sensodrive.btn_clear_error.blockSignals(True)
    #                     tab_sensodrive.lbl_sensodrive_state.setStyleSheet("background-color: orange")
    #                     tab_sensodrive.lbl_sensodrive_state.setText('Off')
    #                 elif inputs.current_state == 0x14:
    #                     tab_sensodrive.btn_on.setEnabled(False)
    #                     tab_sensodrive.btn_on.setStyleSheet(None)
    #                     tab_sensodrive.btn_on.blockSignals(True)
    #                     tab_sensodrive.btn_off.setEnabled(True)
    #                     tab_sensodrive.btn_off.blockSignals(False)
    #                     tab_sensodrive.btn_clear_error.setEnabled(False)
    #                     tab_sensodrive.btn_clear_error.blockSignals(True)
    #                     tab_sensodrive.lbl_sensodrive_state.setStyleSheet("background-color: lightgreen")
    #                     tab_sensodrive.lbl_sensodrive_state.setText('On')
    #                 elif inputs.current_state == 0x18:
    #                     tab_sensodrive.btn_on.setEnabled(False)
    #                     tab_sensodrive.btn_on.blockSignals(True)
    #                     tab_sensodrive.btn_off.setEnabled(False)
    #                     tab_sensodrive.btn_off.blockSignals(True)
    #                     tab_sensodrive.btn_clear_error.setEnabled(True)
    #                     tab_sensodrive.btn_clear_error.blockSignals(False)
    #                     tab_sensodrive.lbl_sensodrive_state.setStyleSheet("background-color: red")
    #                     tab_sensodrive.lbl_sensodrive_state.setText('Error')
    #
    # def _select_hardware_input_type(self):
    #     """
    #     Fills and opens up the selection dialog of hardware.
    #     :return:
    #     """
    #     self._input_type_dialog.combo_hardware_inputtype.clear()
    #     for hardware_inputs in HardwareInputTypes:
    #         self._input_type_dialog.combo_hardware_inputtype.addItem(hardware_inputs.__str__(),
    #                                                                  userData=hardware_inputs)
    #     self._input_type_dialog.show()
    #
    # def _hardware_input_selected(self):
    #     """
    #     Executes when a hardware input is chosen. Also checks the number of SensoDrives,
    #     currently there is a maximum of 2.
    #     :return:
    #     """
    #     selected_hardware_input = self._input_type_dialog.combo_hardware_inputtype.itemData(
    #         self._input_type_dialog.combo_hardware_inputtype.currentIndex())
    #
    #     # hardcode maximum nr of sensodrives
    #     nr_of_sensodrives = 0
    #     for inputs in self.module_manager.module_settings.inputs.values():
    #         if inputs.input_type == HardwareInputTypes.SENSODRIVE:
    #             nr_of_sensodrives += 1
    #
    #     if selected_hardware_input == HardwareInputTypes.SENSODRIVE and nr_of_sensodrives == 2:
    #         msg_box.setText("""
    #                                     <h3> Number of sensodrives is limited to 2 for now! </h3>
    #                                 """)
    #         msg_box.exec()
    #         return
    #
    #     # module_manager manages adding a new hardware input
    #     from_button = True
    #     self.module_manager.add_hardware_input(selected_hardware_input, from_button)
    #
    # def add_hardware_input(self, settings, from_button):
    #     """
    #     Adds the chosen hardware input
    #     :param settings: chosen hardware input settings
    #     :param from_button: boolean that says whether the settings dialog should open or not
    #     :return:
    #     """
    #     input_type = HardwareInputTypes(settings.input_type)
    #
    #     # Adding tab
    #     input_tab = uic.loadUi(input_type.hardware_tab_ui_file)
    #     input_tab.groupBox.setTitle(settings.identifier)
    #
    #     # Connecting buttons
    #     input_dialog = input_type.settings_dialog(module_manager=self.module_manager, settings=settings, parent=self)
    #     input_tab.btn_settings.clicked.connect(input_dialog.show)
    #     input_tab.btn_remove_hardware.clicked.connect(
    #         lambda: self.module_manager.remove_hardware_input(settings.identifier))
    #
    #     if str(HardwareInputTypes.SENSODRIVE) in settings.identifier:
    #         input_tab.btn_on.clicked.connect(lambda: self.module_manager.turn_on_sensodrive(settings.identifier))
    #         input_tab.btn_off.clicked.connect(lambda: self.module_manager.turn_off_sensodrive(settings.identifier))
    #         input_tab.btn_clear_error.clicked.connect(
    #             lambda: self.module_manager.clear_error_sensodrive(settings.identifier))
    #
    #     # add to module_dialog widget
    #     self._hardware_input_tabs_dict[settings.identifier] = input_tab
    #     self.module_widget.hardware_list_layout.addWidget(input_tab)
    #     self._hardware_input_dialogs_dict[settings.identifier] = input_dialog
    #
    #     # open dialog when adding hardware (not sure if this is annoying when loading settings)
    #     if from_button:
    #         input_dialog.show()
    #
    # def remove_hardware_input(self, identifier):
    #     """
    #     Removes the particular hardware input from the dialog and deletes the dialog/hardware tab.
    #     :param identifier:
    #     :return:
    #     """
    #     # remove input tab
    #     self._hardware_input_tabs_dict[identifier].setParent(None)
    #     del self._hardware_input_tabs_dict[identifier]
    #     del self._hardware_input_dialogs_dict[identifier]
