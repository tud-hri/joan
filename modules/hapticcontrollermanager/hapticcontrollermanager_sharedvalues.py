import multiprocessing as mp
from ctypes import *

class HapticControllerManagerSharedVariables:
    def __init__(self):
        self._state = mp.Value(c_int, -2)  # module state [initialized, running, error]
        self._time = mp.Value(c_float, 0.0)
        self.haptic_controllers = {}

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

class FDCASharedVariables:
    def __init__(self):
        self._temp = mp.Value(c_float, 0)

    @property
    def temp(self):
        return self._temp.value

    @temp.setter
    def temp(self, val):
        self._temp.value = val