import os

from PyQt5 import uic, QtWidgets, QtGui, QtCore

from modules.hardwaremanager.action.states import HardwaremanagerStates
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog


class HardwaremanagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MANAGER, module_action=module_action, master_state_handler=master_state_handler, parent=parent)
        self._input_data = {}
        self._inputlist = {}
        self.hardware_widgets = {}

        self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/inputtype.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self._add_selected_input)

        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)

        self.module_widget.btn_add_hardware.clicked.connect(self._input_type_dialog.show)
        self.initialize_widgets_from_settings()

    def _load_settings(self):
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings', filter='*.json')
        if settings_file_to_load:
            self.module_action.load_settings_from_file(settings_file_to_load)
            self.initialize_widgets_from_settings()

    def _save_settings(self):
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings', filter='*.json')
        if file_to_save_in:
            self.module_action.save_settings_to_file(file_to_save_in)

    def _add_selected_input(self):
        # add the selected input to the list
        self.module_action.module_state_handler.request_state_change(HardwaremanagerStates.EXEC.READY)

        new_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/hardware_tab.ui"))

        if "Keyboard" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            device_title = self.module_action.add_a_keyboard(new_widget)
        elif "Joystick" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            device_title = self.module_action.add_a_joystick(new_widget)
        elif "SensoDrive" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            device_title = self.module_action.add_a_sensodrive(new_widget)

        new_widget.groupBox.setTitle(device_title)
        self.module_widget.hardware_list_layout.addWidget(new_widget)

    def initialize_widgets_from_settings(self):
        for keyboard_settings in self.module_action.settings.key_boards:
            new_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/hardware_tab.ui"))
            device_title = self.module_action.add_a_keyboard(new_widget, keyboard_settings=keyboard_settings)
            new_widget.groupBox.setTitle(device_title)
            self.module_widget.hardware_list_layout.addWidget(new_widget)

        for joystick_settings in self.module_action.settings.joy_sticks:
            new_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/hardware_tab.ui"))
            device_title = self.module_action.add_a_joystick(new_widget, joystick_settings=joystick_settings)
            new_widget.groupBox.setTitle(device_title)
            self.module_widget.hardware_list_layout.addWidget(new_widget)

        for sensodrive_settings in self.module_action.settings.sensodrives:
            new_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/hardware_tab.ui"))
            device_title = self.module_action.add_a_sensodrive(new_widget, sensodrive_settings=sensodrive_settings)
            new_widget.groupBox.setTitle(device_title)
            self.module_widget.hardware_list_layout.addWidget(new_widget)

