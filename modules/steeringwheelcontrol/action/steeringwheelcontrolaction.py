from PyQt5 import QtCore

import numpy as np

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .swcontrollertypes import SWControllerTypes
from process import Status
from process.statesenum import State
from .steeringwheelcontrolsettings import SteeringWheelControlSettings, PDcontrollerSettings



class SteeringWheelControlAction(JoanModuleAction):

    def __init__(self, millis=10):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, millis=millis)

        # initialize modulewide state handler
        self.status = Status()

        self.settings = SteeringWheelControlSettings(module_enum=JOANModules.STEERING_WHEEL_CONTROL)

        self._controllers = {}

        self.state_machine.add_state_change_listener(self._state_change_listener)

        #Setup state machine transition conditions
        self.state_machine.set_transition_condition(State.READY, State.RUNNING, self._starting_condition)
        self.state_machine.set_transition_condition(State.RUNNING, State.READY, self._stopping_condition)

        # set up news
        self.data = {}

        self.write_news(news=self.data)

        self.temporary = {}
        self.share_settings(self.settings)

    def _state_change_listener(self):
        sim_data_in = self.read_news(JOANModules.CARLA_INTERFACE)
        hw_data_in = self.read_news(JOANModules.HARDWARE_MANAGER)

        for controller in self._controllers:
            if sim_data_in['vehicles'] is not None:
                self.data[controller] = self._controllers[controller].process(sim_data_in['vehicles'][0], hw_data_in)
            else:
                self.data[controller] = None



        self.write_news(self.data)



    def _starting_condition(self):
        try:
            return True, ''
        except KeyError:
            return False, 'Could not check whether carla is connected'


    def _stopping_condition(self):
        try:
            return True
        except KeyError:
            return False, 'Could not check whether carla is connected'

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """

        sim_data_in = self.read_news(JOANModules.CARLA_INTERFACE)
        hw_data_in = self.read_news(JOANModules.HARDWARE_MANAGER)

        "FOR NOW WE ONLY TRY TO APPLY CONTROLLER ON 1 CAR CAUSE MULTIPLE IS TOTAL MAYHEM"
        for controller in self._controllers:
            if sim_data_in['vehicles'] is not None:
                self.data[controller] = self._controllers[controller].process(sim_data_in['vehicles'][0], hw_data_in)

        # for controller in self._controllers:
        #     if sim_data_in['vehicles'] is not None:
        #         for vehicle_object in sim_data_in['vehicles']:
        #             self.data[controller] = self._controllers[controller].do(vehicle_object, hw_data_in)
        #     else:
        #         self.data[controller] = self._controllers[controller].do(None, hw_data_in)
        print(self.data)

        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        try:
            if self.state_machine.current_state == State.IDLE:
                if len(self._controllers) != 0:
                    for controllers in self._controllers:
                        self._controllers[controllers].initialize()
                    self.state_machine.request_state_change(State.READY, 'You can now run the module')
                else:
                    self.state_machine.request_state_change(State.ERROR, 'No controllers to Initialize')
            elif self.state_machine.current_state == State.ERROR:
                self.state_machine.request_state_change(State.IDLE)

        except RuntimeError:
            return False
        return super().initialize()

    def add_controller(self, controller_type):
        #set the module to idle because we need to reinitialize our controllers!
        self.state_machine.request_state_change(State.IDLE,'You can now add more and reinitialize controllers')
        #add appropriate settings
        if controller_type == SWControllerTypes.PD_SWCONTROLLER:
            self.settings.pd_controllers.append(controller_type.settings)
        if controller_type == SWControllerTypes.FDCA_SWCONTROLLER:
            self.settings.fdca_controllers.append(controller_type.settings)



        number_of_controllers = sum([bool(controller_type.__str__() in k) for k in self._controllers.keys()]) + 1
        controller_list_key = controller_type.__str__() + ' ' + str(number_of_controllers)
        self._controllers[controller_list_key] = controller_type.klass(self, controller_list_key, controller_type.settings)
        self._controllers[controller_list_key].get_controller_tab.controller_groupbox.setTitle(controller_list_key)

        self._controllers[controller_list_key].update_trajectory_list()

        self._state_change_listener()
        return self._controllers[controller_list_key].get_controller_tab

    def remove_controller(self, controller):
        #remove controller from the news
        try:
            del self.data[controller.get_controller_list_key]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        self._controllers[controller.get_controller_list_key].get_controller_tab.setParent(None)
        del self._controllers[controller.get_controller_list_key]

        try:
            del self.data[controller]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        if not self._controllers:
            self.stop()

    def start(self):
        try:
            self.state_machine.request_state_change(State.RUNNING, 'Module Running')
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            try:
                self.state_machine.request_state_change(State.IDLE)
                if len(self._controllers) != 0:
                    self.state_machine.request_state_change(State.READY)
            except RuntimeError:
                return False
        except RuntimeError:
            return False
        return super().stop()

    @property
    def controllers(self):
        return self._controllers

    @property
    def current_controller(self):
        return self._current_controller
