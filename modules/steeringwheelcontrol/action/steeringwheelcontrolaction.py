from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import SteeringWheelControlStates


class SteeringWheelControlAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=10):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.READY)

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
