import os

from PyQt5 import QtWidgets, uic, QtGui

from modules.joanmodules import JOANModules
from .baseswcontroller import BaseSWController

class ManualSWController(BaseSWController):

    def __init__(self, module_action, module_dialog):
        super().__init__(module_action=module_action, module_dialog=module_dialog)
        self.add_tab()

    def do(self, data_in):
        """In manual, the controller has no additional control. We could add some self-centering torque, if we want.
        For now, steeringwheel torque is zero"""
        self.data_out['sw_torque'] = 0

    def add_tab(self):
        """add the manual tab to the steeringwheelcontrol tab"""
        widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../dialog/ui/manual_tab.ui"))
        self.module_dialog.add_tab(widget)

        # add functionality here? Think so, yeah