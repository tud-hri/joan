from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import SteeringWheelControlStates
from .swcontrollertypes import SWContollerTypes
from .swcontrollers.manualswcontroller import ManualSWController

class SteeringWheelControlAction(JoanModuleAction):

    def __init__(self, master_state_handler, millis=10):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.READY)

        self._controllers = {}
        self.add_controller(controller_type=SWContollerTypes.MANUAL)
        self.add_controller(controller_type=SWContollerTypes.PD_SWCONTROLLER)
        self.add_controller(controller_type=SWContollerTypes.FDCA_SWCONTROLLER)

        # set up news
        self.data = {}
        self.data['sw torque'] = 0
        self.write_news(news=self.data)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """

        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        pass

    def add_controller(self, controller_type: SWContollerTypes):
        self._controllers[controller_type] = controller_type.klass(self)

    def start(self):
        try:
            self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.STOPPED)
        except RuntimeError:
            return False
        return super().stop()

    @property
    def controllers(self):
        return self._controllers
