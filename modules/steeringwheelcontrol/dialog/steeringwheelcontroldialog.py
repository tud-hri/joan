import os

from PyQt5 import QtWidgets, uic

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog
from process.statesenum import State


class SteeringWheelControlDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, module_action=module_action, parent=parent)

        # add controller tabs
        # for klass in self.module_action.controllers.values():
        #     self.add_controller_tab(klass)

        # setup dialogs
        self._controller_type_dialog = uic.loadUi(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "sw_controllertype.ui"))
        self._controller_type_dialog.btnbox_sw_controller_type.accepted.connect(self.add_selected_controller_type)

        # add state change listener (for adding controllers)
        self.module_action.state_machine.add_state_change_listener(self._state_change_listener)

        # attach add controller button to code
        self.module_widget.btn_add_sw_controller.clicked.connect(self._controller_type_selection)

        # Settings
        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)


    def _state_change_listener(self):
        """
        This function is called upon whenever the change of the module changes it checks whether its allowed to add
        hardware (only possible in ready or idle states

        """
        current_state = self.module_action.state_machine.current_state
        if current_state == State.READY or current_state == State.IDLE:
            self.module_widget.btn_add_sw_controller.setEnabled(True)
        else:
            self.module_widget.btn_add_sw_controller.setEnabled(False)

    def _load_settings(self):
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings', filter='*.json')
        if settings_file_to_load:
            # remove all current controllers first:
            for controllers in self.module_action._controllers.copy():
                self.module_action.remove_controller(self.module_action._controllers[controllers])



        self.module_action.load_settings_from_file(settings_file_to_load)
        self.initialize_widgets_from_settings()
        self.module_action.initialize()


    def _save_settings(self):
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings', filter='*.json')
        if file_to_save_in:
            self.module_action.save_settings_to_file(file_to_save_in)

    def _controller_type_selection(self):
        self._controller_type_dialog.combobox_sw_controller_type.clear()
        for controllers in SWControllerTypes:
            self._controller_type_dialog.combobox_sw_controller_type.addItem(controllers.__str__(),
                                                                             userData=controllers)
        self._controller_type_dialog.show()

    def add_selected_controller_type(self):
        chosen_controller = self._controller_type_dialog.combobox_sw_controller_type.itemData(
            self._controller_type_dialog.combobox_sw_controller_type.currentIndex())
        new_controller_widget = self.module_action.add_controller(chosen_controller)
        self.module_widget.sw_controller_list_layout.addWidget(new_controller_widget)


    def initialize_widgets_from_settings(self):
        for pd_controller_settings in self.module_action.settings.pd_controllers:
            new_controller_widget = self.module_action.add_controller(SWControllerTypes.PD_SWCONTROLLER, pd_controller_settings)
            self.module_widget.sw_controller_list_layout.addWidget(new_controller_widget)
        for fdca_controller_settings in self.module_action.settings.fdca_controllers:
            new_controller_widget = self.module_action.add_controller(SWControllerTypes.FDCA_SWCONTROLLER, fdca_controller_settings)
            self.module_widget.sw_controller_list_layout.addWidget(new_controller_widget)




    def apply_selected_controller(self):
        vehicle_list = self.module_action.update_vehicle_list()
        if vehicle_list is not None:
            if vehicle_list[0].spawned is True:
                current_widget = self.module_widget.controller_tab_widgets.currentWidget()
                for key, value in self.module_action.controllers.items():
                    if current_widget is value.get_controller_tab:
                        self.module_action.set_current_controller(key)
                        self.module_widget.lbl_current_controller.setText("Current controller: " + str(key))
                        if self.module_action.state_machine.current_state is not State.Running:
                            self.module_action.state_machine.request_state_change(State.READY)
            else:
                self.module_action.state_machine.request_state_change(State.ERROR)
                answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                       'You cannot apply a controller if car 1 is not spawned!',
                                                       buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                if answer == QtWidgets.QMessageBox.Cancel:
                    return
        else:
            self.module_action.state_machine.request_state_change(State.ERROR)
            answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                   'No vehicles available dude.',
                                                   buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Cancel:
                return
