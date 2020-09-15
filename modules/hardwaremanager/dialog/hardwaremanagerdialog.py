import os

from PyQt5 import uic

from modules.joanmodules import JOANModules
from core.joanmoduleaction import JoanModuleAction
from core.joanmoduledialog import JoanModuleDialog
from core.statesenum import State
from modules.hardwaremanager.action.hwinputtypes import HardwareInputTypes

class HardwareManagerDialog(JoanModuleDialog):
    """
    This class is the actual dialog you see when you open up the module. Mostly this class serves as a
    connection between the user and the 'brains', which is the action module.
    """

    def __init__(self, module_action: JoanModuleAction, parent=None):
        """
        Initializes the class
        :param module_action:
        :param parent:
        """
        super().__init__(module=JOANModules.HARDWARE_MANAGER, module_action=module_action, parent=parent)

        # initialize dicts
        self._input_data = {}
        self._input_list = {}
        self.hardware_widgets = {}

        # setup dialogs
        self._input_type_dialog = uic.loadUi(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/inputtype.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self.add_selected_hardware_input)

        # connect buttons
        self.module_widget.btn_add_hardware.clicked.connect(self._hardware_input_selection)

    def handle_state_change(self):
        """
        This function is called upon whenever the change of the module changes it checks whether its allowed to add
        hardware (only possible in ready or idle states

        """
        super().handle_state_change()

        current_state = self.module_action.state_machine.current_state
        if current_state == State.READY or current_state == State.IDLE:
            self.module_widget.btn_add_hardware.setEnabled(True)
        else:
            self.module_widget.btn_add_hardware.setEnabled(False)

    def _hardware_input_selection(self):
        self._input_type_dialog.combo_hardware_inputtype.clear()
        for hardware_inputs in HardwareInputTypes:
            self._input_type_dialog.combo_hardware_inputtype.addItem(hardware_inputs.__str__(),
                                                                             userData=hardware_inputs)
        self._input_type_dialog.show()

    def add_selected_hardware_input(self):
        chosen_hardware_input = self._input_type_dialog.combo_hardware_inputtype.itemData(
            self._input_type_dialog.combo_hardware_inputtype.currentIndex())
        self.module_action.add_hardware_input(chosen_hardware_input)


