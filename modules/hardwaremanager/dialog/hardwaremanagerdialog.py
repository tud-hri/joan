from process.joanmoduledialog import JoanModuleDialog
import os

from PyQt5 import uic

from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog

from modules.hardwaremanager.action.states import HardwaremanagerStates


class HardwaremanagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MANAGER, module_action=module_action, parent=parent)
    #def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
    #    super().__init__(module=JOANModules.HARDWARE_MANAGER, module_action=module_action, master_state_handler=master_state_handler, parent=parent)

        self._input_data = {}
        self._inputlist = {}
        self.hardware_widgets = {}

        self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/UIs/inputtype.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.selected_input)

        # self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.do)
        self.module_widget.btn_add_hardware.clicked.connect(self._input_type_dialog.show)
        
    def selected_input(self):
        # add the selected input to the list
        self.module_action.module_state_handler.request_state_change(HardwaremanagerStates.EXEC.READY)
        self.hardware_widgets = self.module_action.selected_input(self._input_type_dialog.combo_hardware_inputtype.currentText())
        self.module_widget.hardware_list_layout.addWidget(self.hardware_widgets[list(self.hardware_widgets.keys())[-1]])
        self.module_action.do()
