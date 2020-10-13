import multiprocessing as mp
from ctypes import *


class TemplateMPSharedValues:
    def __init__(self):
        self._state = mp.Value(c_int, 0)             # module state [idle, running, error]

        self._time = mp.Value(c_float, 0.0)          # state

    @property
    def state(self):
        return self._state.value

    @state.setter
    def state(self, var):
        self._state.value = var

    @property
    def time(self):
        return self._time.value