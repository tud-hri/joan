import multiprocessing as mp
from ctypes import *

from core.modulesharedvariables import ModuleSharedVariables
from core.sharedvariables import SharedVariables


class CarlaInterfaceSharedVariables(ModuleSharedVariables):
    """
    CarlaInterfaceSharedVariables module, inherits from the ModuleSharedVariables
    """
    def __init__(self):
        super().__init__()
        self.agents = {}


class VehicleSharedVariables(SharedVariables):
    """
    Holds shared variables
    """
    def __init__(self):
        self._transform = mp.Array(c_float, 6)
        self._rear_axle_position = mp.Array(c_float, 3)
        self._velocities_in_world_frame = mp.Array(c_float, 6)
        self._velocities_in_vehicle_frame = mp.Array(c_float, 3)
        self._accelerations = mp.Array(c_float, 3)
        self._applied_input = mp.Array(c_float, 5)
        self._max_steering_angle = mp.Value(c_float)

        # road data for controller plotter
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
    def rear_axle_position(self):
        return self._rear_axle_position[:]

    @rear_axle_position.setter
    def rear_axle_position(self, val):
        self._rear_axle_position[:] = val

    @property
    def velocities_in_world_frame(self):
        return self._velocities_in_world_frame[:]

    @velocities_in_world_frame.setter
    def velocities_in_world_frame(self, val):
        self._velocities_in_world_frame[:] = val

    @property
    def velocities_in_vehicle_frame(self):
        return self._velocities_in_vehicle_frame[:]

    @velocities_in_vehicle_frame.setter
    def velocities_in_vehicle_frame(self, val):
        self._velocities_in_vehicle_frame[:] = val

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
    def max_steering_angle(self):
        return self._max_steering_angle.value

    @max_steering_angle.setter
    def max_steering_angle(self, val):
        self._max_steering_angle.value = val

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
