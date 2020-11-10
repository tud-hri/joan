import multiprocessing as mp
from ctypes import *

from core.modulesharedvariables import ModuleSharedVariables


class CarlaInterfaceSharedVariables(ModuleSharedVariables):
    def __init__(self):
        super().__init__()
        self._state = mp.Value(c_int, -2)  # module state [initialized, running, error]
        self.agents = {}


class EgoVehicleSharedVariables:
    def __init__(self):
        self._transform = mp.Array(c_float, 6)
        self._velocities = mp.Array(c_float, 6)
        self._accelerations = mp.Array(c_float, 3)
        self._applied_input = mp.Array(c_float, 5)

        #road data for controller plotter
        self._data_road_x = mp.Array(c_float, 50)
        self._data_road_x_inner = mp.Array(c_float, 50)
        self._data_road_x_outer = mp.Array(c_float, 50)
        self._data_road_y = mp.Array(c_float, 50)
        self._data_road_y_inner = mp.Array(c_float, 50)
        self._data_road_y_outer = mp.Array(c_float, 50)
        self._data_road_psi = mp.Array(c_float, 50)
        self._data_road_lanewidth = mp.Array(c_float, 50)

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

    @property
    def data_road_x(self):
        return self._data_road_x[:]

    @data_road_x.setter
    def data_road_x(self, val):
        self._data_road_x[:] = val

    @property
    def data_road_x_inner(self):
        return self._data_road_x_inner[:]

    @data_road_x_inner.setter
    def data_road_x_inner(self, val):
        self._data_road_x_inner[:] = val

    @property
    def data_road_x_outer(self):
        return self._data_road_x_outer[:]

    @data_road_x_outer.setter
    def data_road_x_outer(self, val):
        self._data_road_x_outer[:] = val

    @property
    def data_road_y(self):
        return self._data_road_y[:]

    @data_road_y.setter
    def data_road_y(self, val):
        self._data_road_y[:] = val

    @property
    def data_road_y_inner(self):
        return self._data_road_y_inner[:]

    @data_road_y_inner.setter
    def data_road_y_inner(self, val):
        self._data_road_y_inner[:] = val

    @property
    def data_road_y_outer(self):
        return self._data_road_y_outer[:]

    @data_road_y_outer.setter
    def data_road_y_outer(self, val):
        self._data_road_y_outer[:] = val

    @property
    def data_road_psi(self):
        return self._data_road_psi[:]

    @data_road_psi.setter
    def data_road_psi(self, val):
        self._data_road_psi[:] = val

    @property
    def data_road_lanewidth(self):
        return self._data_road_lanewidth[:]

    @data_road_lanewidth.setter
    def data_road_lanewidth(self, val):
        self._data_road_lanewidth[:] = val

