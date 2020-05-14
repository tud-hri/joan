import os

from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from .baseswcontroller import BaseSWController

class PDSWController(BaseSWController):

    def __init__(self, module_action):
        super().__init__(controller_type=SWContollerTypes.PD_SWCONTROLLER, module_action=module_action)

        # default controller values
        self._t_lookahead = 0.6
        self._k_p = 8
        self._k_d = 1
        self._w_lat = 1
        self._w_heading = 2
        self.set_default_parameter_values()

        # connect widgets
        self._controller_tab.btn_apply.clicked.connect(self.get_set_parameter_values_from_ui)
        self._controller_tab.btn_reset.clicked.connect(self.set_default_parameter_values)

    def do(self, data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""

        self.data_out['sw_torque'] = 0

    def get_set_parameter_values_from_ui(self):
        """update controller parameters from ui"""
        self._t_lookahead = float(self._controller_tab.edit_t_ahead.text())
        self._k_p = float(self._controller_tab.edit_gain_prop.text())
        self._k_d = float(self._controller_tab.edit_gain_deriv.text())
        self._w_lat = float(self._controller_tab.edit_weight_lat.text())
        self._w_heading = float(self._controller_tab.edit_weight_heading.text())

        self.update_ui()

    def update_ui(self):
        """update the labels and line edits in the controller_tab with the latest values"""

        self._controller_tab.edit_gain_prop.setText(str(self._k_p))
        self._controller_tab.edit_gain_deriv.setText(str(self._k_d))
        self._controller_tab.edit_weight_lat.setText(str(self._w_lat))
        self._controller_tab.edit_weight_heading.setText(str(self._w_heading))
        self._controller_tab.edit_t_ahead.setText(str(self._t_lookahead))

        # update the current controller settings
        self._controller_tab.lbl_current_gain_prop.setText(str(self._k_p))
        self._controller_tab.lbl_current_gain_deriv.setText(str(self._k_d))
        self._controller_tab.lbl_current_weight_lat.setText(str(self._w_lat))
        self._controller_tab.lbl_current_weight_heading.setText(str(self._w_heading))
        self._controller_tab.lbl_current_t_lookahead.setText(str(self._t_lookahead))

    def set_default_parameter_values(self):
        """set the default controller parameters
        In the near future, this should be from the controller settings class
        """
        
        # default values
        self._t_lookahead = 0.6
        self._k_p = 8
        self._k_d = 1
        self._w_lat = 1
        self._w_heading = 2

        self.update_ui()
        self.get_set_parameter_values_from_ui()
