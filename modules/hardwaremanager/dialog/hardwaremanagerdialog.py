import os

from PyQt5 import uic, QtWidgets

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog
from process.statesenum import State


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
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/ui/inputtype.ui"))
        self._input_type_dialog.btns_hardware_inputtype.accepted.connect(self._add_selected_input)

        self.initialize_widgets_from_settings()

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

    def _load_settings(self):
        """
        Loads settings from json file.
        :return:
        """
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings',
                                                                         os.path.join(self.module_action.module_path,
                                                                                      'action'),
                                                                         filter='*.json')
        if settings_file_to_load:

            # remove all current hardware elements first
            while self.module_widget.hardware_list_layout.count():
                hardware_tab_widget = self.module_widget.hardware_list_layout.takeAt(0).widget()
                hardware_title = hardware_tab_widget.groupBox.title()
                hardware_tab_widget.setParent(None)
                self.module_action.remove(hardware_title)

            self.module_action.load_settings(settings_file_to_load)
            self.initialize_widgets_from_settings()

    def _add_selected_input(self):
        """
        Adds the selected input
        :return:
        """
        # whenever we add an input go back to the IDLE state because we need to reinitialize this new hardware
        self.module_action.state_machine.request_state_change(State.IDLE, 'You can now add more hardware')
        # add the selected input to the list

        if "Keyboard" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/ui/hardware_tab.ui"))
            device_title = self.module_action.add_a_keyboard(new_widget)
        elif "Joystick" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/ui/hardware_tab.ui"))
            device_title = self.module_action.add_a_joystick(new_widget)
        elif "SensoDrive" in self._input_type_dialog.combo_hardware_inputtype.currentText():
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/ui/hardware_tab_sensodrive.ui"))
            device_title = self.module_action.add_a_sensodrive(new_widget)

        self.module_action.input_devices_classes[device_title].settings_dialog.show()

        ## This is a temporary fix so that we cannot add another sensodrive which will make pcan crash because we only have one PCAN usb interface dongle
        ## TODO find a more elegant solution that just goes into error state when trying to add more sensodrives than dongles
        if device_title != 'DO_NOT_ADD':
            new_widget.groupBox.setTitle(device_title)
            self.module_widget.hardware_list_layout.addWidget(new_widget)
        else:
            self.module_action.state_machine.request_state_change(State.ERROR, 'Currently only 2 sensodrives are supported')

        self.module_action._state_change_listener()

    def initialize_widgets_from_settings(self):
        """
        Initializes the widgets from loaded settings.
        :return:
        """
        for keyboard_settings in self.module_action.settings.key_boards:
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/ui/hardware_tab.ui"))
            device_title = self.module_action.add_a_keyboard(new_widget, keyboard_settings=keyboard_settings)
            new_widget.groupBox.setTitle(device_title)
            self.module_widget.hardware_list_layout.addWidget(new_widget)

        for joystick_settings in self.module_action.settings.joy_sticks:
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/ui/hardware_tab.ui"))
            device_title = self.module_action.add_a_joystick(new_widget, joystick_settings=joystick_settings)
            new_widget.groupBox.setTitle(device_title)
            self.module_widget.hardware_list_layout.addWidget(new_widget)

        for sensodrive_settings in self.module_action.settings.sensodrives:
            new_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../action/ui/hardware_tab_sensodrive.ui"))
            device_title = self.module_action.add_a_sensodrive(new_widget, sensodrive_settings=sensodrive_settings)
            new_widget.groupBox.setTitle(device_title)
            self.module_widget.hardware_list_layout.addWidget(new_widget)
