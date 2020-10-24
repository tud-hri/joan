import multiprocessing as mp
from ctypes import *


class HardwareMPSharedValues:
    def __init__(self):
        self._state = mp.Value(c_int, -2)  # module state [idle, running, error]
        self._time = mp.Value(c_float, 0.0)

        self.init_event = mp.Event()
        self.close_event = mp.Event()
        self.turn_on_event = mp.Event()
        self.update_shared_values_from_settings_event = mp.Event()
        self.turn_off_event = mp.Event()
        self.clear_error_event = mp.Event()

        # for testing purposes
        self.keyboards = {}  # {"keyboard3": KeyboardSharedValues()}
        self.joysticks = {}
        self.sensodrives = {}

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


class KeyboardSharedValues:  # TODO: deze drie zijn excact hetzelfde, gaan we hier ooit not onderscheid in maken? Anders samenvoegen tot 1
    def __init__(self):
        self._steering_angle = mp.Value(c_float, 0.0)
        self._throttle = mp.Value(c_float, 0.0)
        self._brake = mp.Value(c_float, -9.9)
        self._reverse = mp.Value(c_bool, False)
        self._handbrake = mp.Value(c_bool, False)

    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, val):
        self._steering_angle.value = val

    @property
    def throttle(self):
        return self._throttle.value

    @throttle.setter
    def throttle(self, val):
        self._throttle.value = val

    @property
    def brake(self):
        return self._brake.value

    @brake.setter
    def brake(self, val):
        self._brake.value = val

    @property
    def reverse(self):
        return self._reverse.value

    @reverse.setter
    def reverse(self, val):
        self._reverse.value = val

    @property
    def handbrake(self):
        return self._handbrake.value

    @handbrake.setter
    def handbrake(self, val):
        self._handbrake.value = val


class JoystickSharedValues:
    def __init__(self):
        self._steering_angle = mp.Value(c_float, 0.0)
        self._throttle = mp.Value(c_float, 0.0)
        self._brake = mp.Value(c_float, -9.9)
        self._reverse = mp.Value(c_bool, False)
        self._handbrake = mp.Value(c_bool, False)


    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, val):
        self._steering_angle.value = val

    @property
    def throttle(self):
        return self._throttle.value

    @throttle.setter
    def throttle(self, val):
        self._throttle.value = val

    @property
    def brake(self):
        return self._brake.value

    @brake.setter
    def brake(self, val):
        self._brake.value = val

    @property
    def reverse(self):
        return self._reverse.value

    @reverse.setter
    def reverse(self, val):
        self._reverse.value = val

    @property
    def handbrake(self):
        return self._handbrake.value

    @handbrake.setter
    def handbrake(self, val):
        self._handbrake.value = val


class SensoDriveSharedValues:
    """"
    This class contains all the variables that are shared between the seperate hardware communication core and the
    main JOAN core.
    """

    def __init__(self):
        self._steering_angle = mp.Value(c_float, 0.0)
        self._throttle = mp.Value(c_float, 0.0)
        self._brake = mp.Value(c_float, -9.9)
        self._reverse = mp.Value(c_bool, False)
        self._handbrake = mp.Value(c_bool, False)

        self._init_event = mp.Event()

    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, val):
        self._steering_angle.value = val

    @property
    def throttle(self):
        return self._throttle.value

    @throttle.setter
    def throttle(self, val):
        self._throttle.value = val

    @property
    def brake(self):
        return self._brake.value

    @brake.setter
    def brake(self, val):
        self._brake.value = val

    @property
    def reverse(self):
        return self._reverse.value

    @reverse.setter
    def reverse(self, val):
        self._reverse.value = val

    @property
    def handbrake(self):
        return self._handbrake.value

    @handbrake.setter
    def handbrake(self, val):
        self._handbrake.value = val
