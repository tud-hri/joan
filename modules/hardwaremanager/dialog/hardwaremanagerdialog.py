import os

from PyQt5 import uic

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

        # self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.do)
        self.module_widget.btn_add_hardware.clicked.connect(self._input_type_dialog.show)
        self.initialize_widgets_from_settings()

    def _add_selected_input(self):
        # add the selected input to the list
        self.module_action.module_state_handler.request_state_change(HardwaremanagerStates.EXEC.READY)

        new_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/hardware_tab.ui"))

        if "Keyboard" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            device_title = self.module_action.add_a_keyboard(new_widget)
        elif "Joystick" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            device_title = self.module_action.add_a_joystick(new_widget)

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
