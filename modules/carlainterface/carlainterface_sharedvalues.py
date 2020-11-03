import multiprocessing as mp
from ctypes import *


class CarlaInterfaceSharedVariables:
    def __init__(self):
        self._state = mp.Value(c_int, -2)  # module state [initialized, running, error]
        self._time = mp.Value(c_float, 0.0)
        self.agents = {}

    @property
    def state(self):
        return self._state.value

    @state.setter
    def state(self, val):
        self._state.value = val

    @property
    def time(self):
        return self._time.value

    @time.setter
    def time(self, val):
        self._time.value = val

class EgoVehicleSharedVariables:
    def __init__(self):
        self._transform = mp.Array(c_float, 6)
        self._velocities = mp.Array(c_float, 6)
        self._accelerations = mp.Array(c_float, 3)
        self._applied_input = mp.Array(c_float, 5)

    @property
    def transform(self):
        return self._transform[:]

    @transform.setter
    def transform(self, val):
        self._transform[:] = val

    @property
    def velocities(self):
        return self._velocities[:]

    @velocities.setter
    def velocities(self, val):
        self._velocities[:] = val

    @property
    def accelerations(self):
        return self._accelerations[:]

    @accelerations.setter
    def accelerations(self, val):
        self._accelerations[:] = val

    @property
    def applied_input(self):
        return self._applied_input[:]

    @applied_input.setter
    def applied_input(self, val):
        self._applied_input[:] = val

