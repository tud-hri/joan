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
        self._k_y = mp.Value(c_float, 0)
        self._k_psi = mp.Value(c_float, 0)
        self._lohs = mp.Value(c_float, 0)
        self._sohf = mp.Value(c_float, 0)
        self._loha = mp.Value(c_float, 0)

    @property
    def temp(self):
        return self._temp.value

    @temp.setter
    def temp(self, val):
        self._temp.value = val

    @property
    def k_y(self):
        return self._k_y.value

    @k_y.setter
    def k_y(self, val):
        self._k_y.value = val

    @property
    def k_psi(self):
        return self._k_psi.value

    @k_psi.setter
    def k_psi(self, val):
        self._k_psi.value = val

    @property
    def lohs(self):
        return self._lohs.value

    @lohs.setter
    def lohs(self, val):
        self._lohs.value = val

    @property
    def sohf(self):
        return self._sohf.value

    @sohf.setter
    def sohf(self, val):
        self._sohf.value = val

    @property
    def loha(self):
        return self._loha.value

    @loha.setter
    def loha(self, val):
        self._loha.value = val