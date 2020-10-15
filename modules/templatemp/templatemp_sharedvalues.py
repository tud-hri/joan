import multiprocessing as mp
from ctypes import *


class TemplateMPSharedValues:
    def __init__(self):
        self._state = mp.Value(c_int, -2)  # module state [idle, running, error]
        self._time = mp.Value(c_float, 0.0)

    def destroy(self):
        print('destroying')

    def __del__(self):
        # Dit is niet betrouwbaar blijkkbaar moet je dit nooit doen, __del__ word niet altijd aangeroepen als je del object doet
        print("SharedValues deleted")
        pass

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
