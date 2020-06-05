from PyQt5 import QtCore

import numpy as np

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import SteeringWheelControlStates
from .swcontrollertypes import SWContollerTypes
from .swcontrollers.manualswcontroller import ManualSWController


class SteeringWheelControlAction(JoanModuleAction):

    def __init__(self, millis=10):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, millis=millis)

        self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.READY)

        self._controllers = {}
        self.add_controller(controller_type=SWContollerTypes.MANUAL)
        self.add_controller(controller_type=SWContollerTypes.PD_SWCONTROLLER)
        self.add_controller(controller_type=SWContollerTypes.FDCA_SWCONTROLLER)

        self._current_controller = None
        self.set_current_controller(SWContollerTypes.MANUAL)

        # set up news
        self.data = {}
        self.data['sw_torque'] = 0
        self.data['lat_error'] = 0
        self.data['heading_error'] = 0
        self.data['lat_error_rate'] = 0
        self.data['heading_error_rate'] = 0
        self.write_news(news=self.data)

    def update_vehicle_list(self):
        carla_data = self.read_news(JOANModules.CARLA_INTERFACE)
        vehicle_list = carla_data['vehicles']
        return vehicle_list

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """

        sim_data_in = self.read_news(JOANModules.CARLA_INTERFACE)
        hw_data_in = self.read_news(JOANModules.HARDWARE_MANAGER)

        data_out = self._current_controller.do(sim_data_in, hw_data_in)

        # extract from controller's output data_out
        self.data['sw_torque'] = data_out['sw_torque']
        # self.data['lat_error'] = data_out['lat_error']
        # self.data['heading_error'] = data_out['heading_error']
        # self.data['lat_error_rate'] = data_out['lat_error_rate']
        # self.data['heading_error_rate'] = data_out['heading_error_rate']

        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """

    def add_controller(self, controller_type: SWContollerTypes):
        self._controllers[controller_type] = controller_type.klass(self)

    def set_current_controller(self, controller_type: SWContollerTypes):
        self._current_controller = self._controllers[controller_type]
        current_state = self.module_state_handler.get_current_state()

        if current_state is not SteeringWheelControlStates.EXEC.RUNNING:
            self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.READY)

    def start(self):
        try:
            self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.STOPPED)
            self.module_state_handler.request_state_change(SteeringWheelControlStates.EXEC.READY)
        except RuntimeError:
            return False
        return super().stop()

    @property
    def controllers(self):
        return self._controllers

    @property
    def current_controller(self):
        return self._current_controller
