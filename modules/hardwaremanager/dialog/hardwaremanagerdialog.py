import os

from PyQt5 import uic, QtWidgets

from modules.hardwaremanager.action.inputclasses.joansensodrive import JOANSensoDrive
from modules.joanmodules import JOANModules
from core.joanmoduleaction import JoanModuleAction
from core.joanmoduledialog import JoanModuleDialog
from core.statesenum import State


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
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self._add_selected_input)

        # connect buttons
        self.module_widget.btn_add_hardware.clicked.connect(self._input_type_dialog.show)

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

    def _add_selected_input(self):
        """
        Adds the selected input
        :return:
        """
        # whenever we add an input go back to the IDLE state because we need to reinitialize this new hardware
        self.module_action.state_machine.request_state_change(State.IDLE, 'You can now add more hardware')

        # add the selected input to the list
        input_type = self._input_type_dialog.combo_hardware_inputtype.currentText()

        if "Keyboard" in input_type:
            self.module_action.add_a_keyboard()
        elif "Joystick" in input_type:
            self.module_action.add_a_joystick()
        elif "SensoDrive" in input_type:
            if not self.module_action.add_a_sensodrive():
                # TODO find a more elegant solution that just goes into error state when trying to add more sensodrives than dongles
                self.module_action.state_machine.request_state_change(State.ERROR,
                                                                      'Currently only 2 sensodrives are supported')

        # self.module_action.input_devices_classes[device_title].settings_dialog.show()

    def add_device_tab(self, device):
        """add a tab widget for a new keyboard, """
        if not isinstance(device, JOANSensoDrive):
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/hardware_tab.ui"))
        elif isinstance(device, JOANSensoDrive):
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/hardware_tab_sensodrive.ui"))

        new_widget.groupBox.setTitle(device.name)
        self.module_widget.hardware_list_layout.addWidget(new_widget)

        # connect the widget to the device
        device.connect_widget(new_widget)
