import os
import queue

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMessageBox

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from core.statesenum import State
from modules.joanmodules import JOANModules
from modules.npccontrollermanager.npccontrollertypes import NPCControllerTypes

msg_box = QMessageBox()
msg_box.setTextFormat(QtCore.Qt.RichText)


class NPCControllerManagerDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        """
        Initializes the class
        :param module_manager:
        :param parent:
        """
        super().__init__(module=JOANModules.NPC_CONTROLLER_MANAGER, module_manager=module_manager, parent=parent)

        # Loading the inputtype dialog (in which we will be able to add controllers dynamically)
        self._controller_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "select_controller_type.ui"))
        self._controller_type_dialog.button_box.accepted.connect(self._controller_selected)

        # Connect the add controller button to showing our just created controller type dialog
        self.module_widget.btn_add_controller.clicked.connect(self._select_controller_type)
        self._controller_tabs_dict = {}
        self._controller_dialogs_dict = {}

    def update_dialog(self):
        """
        Updates the Dialog, this function is called at a rate of 10Hz.
        :return:
        """
        difference_dict = {k: self._controller_tabs_dict[k] for k in set(self._controller_tabs_dict) - set(self.module_manager.module_settings.controllers)}
        for key in difference_dict:
            self.remove_controller(key)

        for controller_identifier, controller_settings in self.module_manager.module_settings.controllers.items():
            if controller_identifier not in self._controller_tabs_dict.keys():
                self.add_controller(controller_identifier, controller_settings, False)

    def _handle_state_change(self):
        """
        We only want to be able to add controllers when we are in the stopped state, therefore we add this to the state
        change listener for this module. We should however not forget also calling the super()._handle_state_change()
        method.
        """
        super()._handle_state_change()

        state = self.module_manager.state_machine.current_state
        # joysticks and keyboards
        self.module_widget.btn_add_controller.setEnabled(state == State.STOPPED)

        for _, controller_tab in self._controller_tabs_dict.items():
            controller_tab.btn_remove_controller.setEnabled(state == State.STOPPED)
            controller_tab.btn_settings.setEnabled(state == State.STOPPED)

    def _select_controller_type(self):
        """
        Fills and opens up the selection dialog of controllers.
        :return:
        """
        self._controller_type_dialog.combo_controller_type.clear()
        for controller_type in NPCControllerTypes:
            self._controller_type_dialog.combo_controller_type.addItem(controller_type.__str__(), userData=controller_type)
        self._controller_type_dialog.show()

    def _controller_selected(self):
        """
        Executes when a hardware input is chosen.
        :return:
        """
        selected_controller_type = self._controller_type_dialog.combo_controller_type.itemData(
            self._controller_type_dialog.combo_controller_type.currentIndex())

        # module_manager manages adding a new hardware input
        from_button = True
        self.module_manager.add_controller(selected_controller_type, show_settings_dialog=True)

    def add_controller(self, identifier, controller_settings, show_settings_dialog):
        controller_type = controller_settings.controller_type

        # Adding tab
        controller_tab = uic.loadUi(controller_type.hardware_tab_ui_file)
        controller_tab.groupBox.setTitle(identifier)

        # Connecting buttons
        controller_dialog = controller_type.settings_dialog(module_manager=self.module_manager, settings=controller_settings, parent=self)
        controller_tab.btn_settings.clicked.connect(controller_dialog.show)
        controller_tab.btn_remove_controller.clicked.connect(lambda: self.module_manager.remove_controller(identifier))

        # add to module_dialog widget
        self._controller_tabs_dict[identifier] = controller_tab
        self.module_widget.controller_list_layout.addWidget(controller_tab)
        self._controller_dialogs_dict[identifier] = controller_dialog

        # open dialog when adding hardware
        if show_settings_dialog:
            controller_dialog.show()

    def remove_controller(self, identifier):
        """
        Removes the particular hardware input from the dialog and deletes the dialog/hardware tab.
        :param identifier:
        :return:
        """
        # remove input tab
        self._controller_tabs_dict[identifier].setParent(None)
        del self._controller_tabs_dict[identifier]
        del self._controller_dialogs_dict[identifier]
