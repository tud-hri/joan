import ctypes

import multiprocessing as mp
from .sharedvariables import SharedVariables


class ModuleSharedVariables(SharedVariables):
    def __init__(self):
        self._state = mp.Value(ctypes.c_int, -2)  # module state [initialized, running, error, stopped]
        self._execution_time = mp.Value(ctypes.c_double)
        self._running_frequency = mp.Value(ctypes.c_double)
        self._time = mp.Value(ctypes.c_uint64)

    @property
    def execution_time(self):
        return self._execution_time.value

    @execution_time.setter
    def execution_time(self, value):
        self._execution_time.value = value

    @property
    def running_frequency(self):
        return self._running_frequency.value

    @running_frequency.setter
    def running_frequency(self, value):
        self._running_frequency.value = value

    @property
    def time(self):
        return self._time.value

    @time.setter
    def time(self, value):
        self._time.value = value

    @property
    def state(self):
        return self._state.value

    @state.setter
    def state(self, val):
        self._state.value = val
