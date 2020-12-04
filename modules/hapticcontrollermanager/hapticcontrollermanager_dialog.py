import os

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules

from PyQt5 import uic
from modules.hapticcontrollermanager.hapticcontrollermanager_controllertypes import HapticControllerTypes
from core.statesenum import State


class HapticControllerManagerDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.HAPTIC_CONTROLLER_MANAGER, module_manager=module_manager, parent=parent)
        """
        Initializes the class
        :param module_manager:
        :param parent:
        """
        # setup dialogs
        self._haptic_controller_type_dialog = uic.loadUi(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "select_haptic_controller.ui"))
        self._haptic_controller_type_dialog.btns_haptic_controller_type_select.accepted.connect(self._haptic_controller_selected)

        # connect buttons
        self.module_widget.btn_add_haptic_controller.clicked.connect(self._select_haptic_controller_type)
        self._haptic_controller_tabs_dict = {}
        self._haptic_controller_dialogs_dict = {}

    def update_dialog(self):
        for controller_settings in self.module_manager.module_settings.haptic_controllers:
            if self.module_manager.module_settings.haptic_controllers[controller_settings].identifier not in self._haptic_controller_tabs_dict:
                self.add_haptic_controller(self.module_manager.module_settings.haptic_controllers[controller_settings], False)
            self._haptic_controller_dialogs_dict[self.module_manager.module_settings.haptic_controllers[controller_settings].identifier]._display_values(
                self.module_manager.module_settings.haptic_controllers[controller_settings])

    def _handle_state_change(self):
        """"
        This function handles the enabling and disabling of the carla interface change
        """
        super()._handle_state_change()
        if self.module_manager.state_machine.current_state == State.STOPPED:
            self.module_widget.btn_add_haptic_controller.setEnabled(True)
            self.module_widget.btn_add_haptic_controller.blockSignals(False)
            for haptic_controller_tabs in self._haptic_controller_tabs_dict:
                self._haptic_controller_tabs_dict[haptic_controller_tabs].btn_remove_haptic_controller.setEnabled(True)
                self._haptic_controller_tabs_dict[haptic_controller_tabs].btn_remove_haptic_controller.blockSignals(False)
        else:
            self.module_widget.btn_add_haptic_controller.setEnabled(False)
            self.module_widget.btn_add_haptic_controller.blockSignals(True)
            for haptic_controller_tabs in self._haptic_controller_tabs_dict:
                self._haptic_controller_tabs_dict[haptic_controller_tabs].btn_remove_haptic_controller.setEnabled(False)
                self._haptic_controller_tabs_dict[haptic_controller_tabs].btn_remove_haptic_controller.blockSignals(True)

        for haptic_controller_tabs in self._haptic_controller_tabs_dict:
            self._haptic_controller_tabs_dict[haptic_controller_tabs].btn_settings.setEnabled(True)
            self._haptic_controller_tabs_dict[haptic_controller_tabs].btn_settings.blockSignals(False)

    def _select_haptic_controller_type(self):
        self._haptic_controller_type_dialog.combo_haptic_controller_type.clear()
        for haptic_controllers in HapticControllerTypes:
            self._haptic_controller_type_dialog.combo_haptic_controller_type.addItem(haptic_controllers.__str__(), userData=haptic_controllers)
        self._haptic_controller_type_dialog.show()

    def _haptic_controller_selected(self):
        selected_haptic_controller = self._haptic_controller_type_dialog.combo_haptic_controller_type.itemData(
            self._haptic_controller_type_dialog.combo_haptic_controller_type.currentIndex())
        # module_manager manages adding a new haptic_controller
        from_button = True
        self.module_manager.add_haptic_controller(selected_haptic_controller, from_button)

    def add_haptic_controller(self, settings, from_button):
        haptic_controller_type = HapticControllerTypes(settings.haptic_controller_type)

        # Adding tab
        haptic_controller_tab = uic.loadUi(haptic_controller_type.haptic_controller_ui_file)
        haptic_controller_tab.group_haptic_controller.setTitle(settings.identifier)

        # adding dialog
        haptic_controller_dialog = haptic_controller_type.settings_dialog(settings=settings, module_manager=self.module_manager, parent=self)

        # Connecting buttons
        haptic_controller_tab.btn_settings.clicked.connect(haptic_controller_dialog.show)
        haptic_controller_tab.btn_remove_haptic_controller.clicked.connect(lambda: self.module_manager.remove_haptic_controller(settings.identifier))

        # add to module_dialog widget
        self._haptic_controller_tabs_dict[settings.identifier] = haptic_controller_tab
        self.module_widget.haptic_controller_list_layout.addWidget(haptic_controller_tab)
        self._haptic_controller_dialogs_dict[settings.identifier] = haptic_controller_dialog

        if from_button:
            haptic_controller_dialog.show()

    def remove_haptic_controller(self, identifier):
        # remove haptic_controller tab
        self._haptic_controller_tabs_dict[identifier].setParent(None)
        del self._haptic_controller_tabs_dict[identifier]
        del self._haptic_controller_dialogs_dict[identifier]
