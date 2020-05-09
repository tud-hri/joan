import abc

from PyQt5 import QtWidgets, uic

from modules.joanmodules import JOANModules
from modules.steeringwheelcontrol.action.swcontrollertypes import SWContollerTypes

class BaseSWController:
    def __init__(self, controller_type: SWContollerTypes, module_action: JOANModules):
        self._action = module_action
        self._controller_type = controller_type
        self._controller_tab = uic.loadUi(self._controller_type.tab_ui_file)

        self._data_in = {}
        self._data_out = {}
        self._data_out['sw_torque'] = 0

    @abc.abstractmethod
    def do(self, data_in):
        """do is called every tick in steeringwheelcontrolaction's do
        this needs to be implemented by children of BaseSWController
        """
        return self._data_out

    @property
    def get_controller_tab(self):
        return self._controller_tab

    @property
    def name(self):
        return str(self._controller_type)
