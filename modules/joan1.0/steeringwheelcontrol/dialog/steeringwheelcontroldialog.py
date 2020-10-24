import os

from PyQt5 import QtWidgets, uic

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from core.joanmoduleaction import JoanModuleAction
from core.joanmoduledialog import JoanModuleDialog
from core.statesenum import State


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
        self.module_action.state_machine.add_state_change_listener(self.handle_state_change)

        # attach add controller button to code
        self.module_widget.btn_add_sw_controller.clicked.connect(self._controller_type_selection)

    def handle_state_change(self):
        """
        This function is called upon whenever the change of the module changes it checks whether its allowed to add
        hardware (only possible in ready or initialized states

        """
        super().handle_state_change()

        current_state = self.module_action.state_machine.current_state
        if current_state == State.READY or current_state == State.INITIALIZED:
            self.module_widget.btn_add_sw_controller.setEnabled(True)
        else:
            self.module_widget.btn_add_sw_controller.setEnabled(False)

    def _controller_type_selection(self):
        self._controller_type_dialog.combobox_sw_controller_type.clear()
        for controllers in SWControllerTypes:
            self._controller_type_dialog.combobox_sw_controller_type.addItem(controllers.__str__(),
                                                                             userData=controllers)
        self._controller_type_dialog.show()

    def add_selected_controller_type(self):
        chosen_controller = self._controller_type_dialog.combobox_sw_controller_type.itemData(
            self._controller_type_dialog.combobox_sw_controller_type.currentIndex())
        self.module_action.add_controller(chosen_controller)

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
