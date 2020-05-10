import os

from PyQt5 import QtCore

from process import State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from modules.steeringwheelcontrol.action.states import SteeringWheelControlStates
from modules.steeringwheelcontrol.action.steeringwheelcontrolaction import SteeringWheelControlAction


class SteeringWheelControlDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, module_action=module_action, master_state_handler=master_state_handler, parent=parent)

        # add controller tabs
        for klass in self.module_action.controllers.values():
            self.add_controller_tab(klass)

        self.module_widget.lbl_current_controller.setText("Current controller: " + self.module_action.current_controller.name)

        self.module_widget.btn_apply_controller.clicked.connect(self.apply_selected_controller)
  
    def add_controller_tab(self, controller):
        self.module_widget.controller_tab_widgets.addTab(controller.get_controller_tab, controller.name)
        
    def apply_selected_controller(self):
        current_widget = self.module_widget.controller_tab_widgets.currentWidget()

        for key, value in self.module_action.controllers.items():
            if current_widget is value.get_controller_tab:
                self.module_action.set_current_controller(key)
                self.module_widget.lbl_current_controller.setText("Current controller: " + str(key))
