import os

from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWControllerTypes
from .baseswcontroller import BaseSWController

class ManualSWController(BaseSWController):

    def __init__(self, module_action, controller_list_key):
        super().__init__(controller_type=SWControllerTypes.MANUAL, module_action=module_action)
        self.module_action = module_action
        # controller list key
        self.controller_list_key = controller_list_key

        self._controller_tab = self.get_controller_tab

    @property
    def get_controller_list_key(self):
        return self.controller_list_key

    def do(self, data_in, hw_data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""
        self._data_out['sw_torque'] = 0
        return self._data_out
