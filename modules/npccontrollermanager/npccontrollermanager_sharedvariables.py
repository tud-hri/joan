import multiprocessing as mp
from ctypes import *

from core.modulesharedvariables import ModuleSharedVariables
from core.sharedvariables import SharedVariables


class NPCControllerManagerSharedVariables(ModuleSharedVariables):
    def __init__(self):
        """"
        This class contains all the variables that are shared between the controller module and the other JOAN modules.
        """
        super().__init__()
        self.controllers = {}


class NPCControllerSharedVariables(SharedVariables):
    """"
    This class contains all the variables that are shared between the controller module and the other JOAN modules.
    """

    def __init__(self):
        self._steering_angle = mp.Value(c_float, 0.0)
        self._throttle = mp.Value(c_float, 0.0)
        self._brake = mp.Value(c_float, -9.9)
        self._reverse = mp.Value(c_bool, False)
        self._handbrake = mp.Value(c_bool, False)
        self._desired_velocity = mp.Value(c_float, 0.0)

    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, val):
        self._steering_angle.value = val

    @property
    def throttle(self):
        return self._throttle.value

    @throttle.setter
    def throttle(self, val):
        self._throttle.value = val

    @property
    def brake(self):
        return self._brake.value

    @brake.setter
    def brake(self, val):
        self._brake.value = val

    @property
    def reverse(self):
        return self._reverse.value

    @reverse.setter
    def reverse(self, val):
        self._reverse.value = val

    @property
    def handbrake(self):
        return self._handbrake.value

    @handbrake.setter
    def handbrake(self, val):
        self._handbrake.value = val

    @property
    def desired_velocity(self):
        return self._desired_velocity.value

    @desired_velocity.setter
    def desired_velocity(self, val):
        self._desired_velocity.value = val
