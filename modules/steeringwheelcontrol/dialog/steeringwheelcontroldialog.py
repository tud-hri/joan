import os

from PyQt5 import QtWidgets, QtGui

from process import State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from modules.steeringwheelcontrol.action.states import SteeringWheelControlStates
from modules.steeringwheelcontrol.action.steeringwheelcontrolaction import SteeringWheelControlAction


class SteeringWheelControlDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, module_action=module_action, parent=parent)

        # add controller tabs
        for klass in self.module_action.controllers.values():
            self.add_controller_tab(klass)

        self.module_widget.lbl_current_controller.setText("Current controller: " + self.module_action.current_controller.name)

        self.module_widget.btn_apply_controller.clicked.connect(self.apply_selected_controller)
        self.module_widget.btn_update_vehicle_list.setEnabled(False)
        self.module_widget.combobox_vehicle_list.setEnabled(False)
        # self.module_widget.btn_update_vehicle_list.clicked.connect(self.update_vehicle_list_dialog)

    def add_controller_tab(self, controller):
        self.module_widget.controller_tab_widgets.addTab(controller.get_controller_tab, controller.name)

    def update_vehicle_list_dialog(self):
        # only add the availability to control the steering wheel if the car is spawned (Is for later implemenation of multi-agent simulator)
        # self.module_widget.combobox_vehicle_list.clear()
        # self.module_widget.combobox_vehicle_list.addItem('None')
        # vehicle_list = self.module_action.update_vehicle_list()
        # if vehicle_list is not None:
        #     for vehicle in vehicle_list:
        #         if vehicle.spawned is True:
        #             self.module_widget.combobox_vehicle_list.addItem(vehicle.vehicle_nr)
        pass

    def apply_selected_controller(self):
        vehicle_list = self.module_action.update_vehicle_list()
        if vehicle_list is not None:
            if vehicle_list[0].spawned is True:
                current_widget = self.module_widget.controller_tab_widgets.currentWidget()
                for key, value in self.module_action.controllers.items():
                    if current_widget is value.get_controller_tab:
                        self.module_action.set_current_controller(key)
                        self.module_widget.lbl_current_controller.setText("Current controller: " + str(key))
                        if self.module_action.module_state_handler.get_current_state() is not SteeringWheelControlStates.EXEC.RUNNING:
                            self.module_action.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.READY)
            else:
                self.module_action.module_state_handler.request_state_change(SteeringWheelControlStates.ERROR)
                answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                       'You cannot apply a controller if car 1 is not spawned!',
                                                       buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                if answer == QtWidgets.QMessageBox.Cancel:
                    return
        else:
            self.module_action.module_state_handler.request_state_change(SteeringWheelControlStates.ERROR)
            answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                   'No vehicles available dude.',
                                                   buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Cancel:
                return
