import multiprocessing as mp
from ctypes import *

from core.modulesharedvariables import ModuleSharedVariables
from core.sharedvariables import SharedVariables


class HapticControllerManagerSharedVariables(ModuleSharedVariables):
    def __init__(self):
        super().__init__()
        self.haptic_controllers = {}

class FDCASharedVariables(SharedVariables):
    def __init__(self):
        # controller parameters
        self._temp = mp.Value(c_float, 0)
        self._k_y = mp.Value(c_float, 0)
        self._k_psi = mp.Value(c_float, 0)
        self._lohs = mp.Value(c_float, 0)
        self._sohf = mp.Value(c_float, 0)
        self._loha = mp.Value(c_float, 0)

        # controller outputs
        self._lat_error = mp.Value(c_float, 0)
        self._sw_des = mp.Value(c_float, 0)
        self._heading_error = mp.Value(c_float, 0)
        self._ff_torque = mp.Value(c_float, 0)
        self._fb_torque = mp.Value(c_float, 0)
        self._loha_torque = mp.Value(c_float, 0)
        self._req_torque = mp.Value(c_float, 0)
        self._x_road = mp.Array(c_float, 50)
        self._y_road = mp.Array(c_float, 50)

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

    @property
    def lat_error(self):
        return self._lat_error.value

    @lat_error.setter
    def lat_error(self, val):
        self._lat_error.value = val

    @property
    def sw_des(self):
        return self._sw_des.value

    @sw_des.setter
    def sw_des(self, val):
        self._sw_des.value = val

    @property
    def heading_error(self):
        return self._heading_error.value

    @heading_error.setter
    def heading_error(self, val):
        self._heading_error.value = val

    @property
    def ff_torque(self):
        return self._ff_torque.value

    @ff_torque.setter
    def ff_torque(self, val):
        self._ff_torque.value = val

    @property
    def fb_torque(self):
        return self._fb_torque.value

    @fb_torque.setter
    def fb_torque(self, val):
        self._fb_torque.value = val

    @property
    def loha_torque(self):
        return self._loha_torque.value

    @loha_torque.setter
    def loha_torque(self, val):
        self._loha_torque.value = val

    @property
    def req_torque(self):
        return self._req_torque.value

    @req_torque.setter
    def req_torque(self, val):
        self._req_torque.value = val

    @property
    def x_road(self):
        return self._x_road[:]

    @x_road.setter
    def x_road(self, val):
        self._x_road[:] = val

    @property
    def y_road(self):
        return self._y_road[:]

    @y_road.setter
    def y_road(self, val):
        self._y_road[:] = val

class TradedControllerSharedVariables(SharedVariables):
    def __init__(self):
        # controller parameters
        self._k_y = mp.Value(c_float, 0)
        self._k_psi = mp.Value(c_float, 0)
        self._kd_y = mp.Value(c_float, 0)
        self._kd_psi = mp.Value(c_float, 0)
        self._alpha = mp.Value(c_float, 0)
        self._tau_th = mp.Value(c_float, 0)

        # controller outputs
        self._lat_error = mp.Value(c_float, 0)
        self._sw_des = mp.Value(c_float, 0)
        self._heading_error = mp.Value(c_float, 0)
        self._ff_torque = mp.Value(c_float, 0)
        self._fb_torque = mp.Value(c_float, 0)
        self._req_torque = mp.Value(c_float, 0)
        self._authority = mp.Value(c_float, 0)
        self._estimated_human_torque = mp.Value(c_float, 0)
        self._x_road = mp.Array(c_float, 50)
        self._y_road = mp.Array(c_float, 50)


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
    def kd_y(self):
        return self._kd_y.value

    @kd_y.setter
    def kd_y(self, val):
        self._kd_y.value = val

    @property
    def kd_psi(self):
        return self._kd_psi.value

    @kd_psi.setter
    def kd_psi(self, val):
        self._kd_psi.value = val

    @property
    def alpha(self):
        return self._alpha.value

    @alpha.setter
    def alpha(self, val):
        self._alpha.value = val

    @property
    def tau_th(self):
        return self._tau_th.value

    @tau_th.setter
    def tau_th(self, val):
        self._tau_th.value = val

    @property
    def lat_error(self):
        return self._lat_error.value

    @lat_error.setter
    def lat_error(self, val):
        self._lat_error.value = val

    @property
    def sw_des(self):
        return self._sw_des.value

    @sw_des.setter
    def sw_des(self, val):
        self._sw_des.value = val

    @property
    def heading_error(self):
        return self._heading_error.value

    @heading_error.setter
    def heading_error(self, val):
        self._heading_error.value = val

    @property
    def ff_torque(self):
        return self._ff_torque.value

    @ff_torque.setter
    def ff_torque(self, val):
        self._ff_torque.value = val

    @property
    def fb_torque(self):
        return self._fb_torque.value

    @fb_torque.setter
    def fb_torque(self, val):
        self._fb_torque.value = val

    @property
    def req_torque(self):
        return self._req_torque.value

    @req_torque.setter
    def req_torque(self, val):
        self._req_torque.value = val

    @property
    def authority(self):
        return self._authority.value

    @authority.setter
    def authority(self, val):
        self._authority.value = val

    @property
    def estimated_human_torque(self):
        return self._estimated_human_torque.value

    @estimated_human_torque.setter
    def estimated_human_torque(self, val):
        self._estimated_human_torque.value = val

    @property
    def x_road(self):
        return self._x_road[:]

    @x_road.setter
    def x_road(self, val):
        self._x_road[:] = val

    @property
    def y_road(self):
        return self._y_road[:]

    @y_road.setter
    def y_road(self, val):
        self._y_road[:] = val

class FDCADuecaSharedVariables(SharedVariables):
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
