import multiprocessing as mp
from ctypes import *


class TemplateMPSharedValues:
    def __init__(self):
        self._state = mp.Value(c_int, -2)  # module state [idle, running, error]
        self._time = mp.Value(c_float, 0.0)
        self._overwrite_with_current_time = mp.Array('c', 30)  # 30=length of string

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

    @property
    def overwrite_with_current_time(self):
        return self._overwrite_with_current_time.value

    @overwrite_with_current_time.setter
    def overwrite_with_current_time(self, val):
        self._overwrite_with_current_time .value = val