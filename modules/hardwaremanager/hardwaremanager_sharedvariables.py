import multiprocessing as mp
from ctypes import *


class HardwareSharedVariables:
    def __init__(self):
        """"
        This class contains all the variables that are shared between the seperate hardware communication core and the
        main JOAN core.
        """
        self._state = mp.Value(c_int, -2)  # module state [initialized, running, error]
        self._time = mp.Value(c_float, 0.0)
        self.inputs = {}

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


class KeyboardSharedVariables:
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


class JoystickSharedVariables:
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


class SensoDriveSharedVariables:
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

        self._measured_torque = mp.Value(c_float, 0.0)
        self._steering_rate = mp.Value(c_float, 0.0)

        self._torque = mp.Value(c_float, 0.0)
        self._damping = mp.Value(c_float, 0.0)
        self._friction = mp.Value(c_float, 0.0)
        self._stiffness = mp.Value(c_float, 0.0)


    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, val):
        self._steering_angle.value = val

    @property
    def steering_rate(self):
        return self._steering_rate.value

    @steering_rate.setter
    def steering_rate(self, var):
        self._steering_rate.value = var

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

    @property
    def measured_torque(self):
        return self._measured_torque.value

    @measured_torque.setter
    def measured_torque(self, var):
        self._measured_torque.value = var

    @property
    def torque(self):
        return self._torque.value

    @torque.setter
    def torque(self, var):
        self._torque.value = var

    @property
    def spring_stiffness(self):
        return self._stiffness.value

    @spring_stiffness.setter
    def spring_stiffness(self, var):
        self._stiffness.value = var

    @property
    def damping(self):
        return self._damping.value

    @damping.setter
    def damping(self, var):
        self._damping.value = var

    @property
    def friction(self):
        return self._friction.value

    @friction.setter
    def friction(self, var):
        self._friction.value = var