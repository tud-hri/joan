import os

from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from .baseswcontroller import BaseSWController

class ManualSWController(BaseSWController):

    def __init__(self, module_action):
        super().__init__(controller_type=SWContollerTypes.MANUAL, module_action=module_action)

    def do(self, data_in, hw_data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""
        self._data_out['sw_torque'] = 0
        return self._data_out
