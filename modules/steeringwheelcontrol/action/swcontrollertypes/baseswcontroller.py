import abc

from modules.joanmodules import JOANModules

class BaseSWController:
    def __init__(self, module_action: JOANModules, module_dialog: JOANModules):
        self.action = module_action
        self.dialog = module_dialog
        
        self.data_in = {}
        self.data_out = {}
        self.data_out['sw_torque'] = 0

    @abc.abstractmethod
    def do(self, data_in):
        """do is called every tick in steeringwheelcontrolaction's do
        this needs to be implemented by children of BaseSWController
        """
        return self.data_out

    @abc.abstractmethod
    def add_tab(self):
        """add a tab in steeringwheelcontroldialog"""

    @abc.abstractmethod
    def remove_tab(self):
        """remove this tab in steeringwheelcontroldialog"""


    