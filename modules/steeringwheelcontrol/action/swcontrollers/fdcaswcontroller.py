import os

from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes
from .baseswcontroller import BaseSWController

class FDCASWController(BaseSWController):

    def __init__(self, module_action):
        super().__init__(controller_type=SWContollerTypes.FDCA_SWCONTROLLER, module_action=module_action)

    def do(self, data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""
        self.data_out['sw_torque'] = 0