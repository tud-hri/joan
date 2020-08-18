import multiprocessing as mp
from modules.hardwaremanager.action.inputclasses.PCANBasic import *

class SensoDriveSharedValues:
    """"
    This class contains all the variables that are shared between the seperate hardware communication process and the
    main JOAN process.
    """

    def __init__(self):
        # Encoder Values
        self._steering_angle = mp.Value(c_float, 0)
        self._throttle = mp.Value(c_float, 0)
        self._brake = mp.Value(c_float, 0)

        # Steering Parameter Values
        self._friction = mp.Value(c_int, 0)
        self._damping = mp.Value(c_int, 0)
        self._spring_stiffness = mp.Value(c_int, 0)
        self._torque = mp.Value(c_int, 0)

        # Extra Info Parameters
        self._measured_torque = mp.Value(c_int, 0)
        self._sensodrive_motorstate = mp.Value(c_int, 0)

        # SensoDrive Settings (torque limits, endstops etc)
        self._endstops = mp.Value(c_int, 0)
        self._torque_limit_between_endstops = mp.Value(c_int, 0)
        self._torque_limit_beyond_endstops = mp.Value(c_int, 0)

        #SensoDrive (ID) or number of sensodrives
        self._sensodrive_ID = mp.Value(c_int,0)

    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, var):
        self._steering_angle.value = var

    @property
    def throttle(self):
        return self._throttle.value

    @throttle.setter
    def throttle(self, var):
        self._throttle.value = var

    @property
    def brake(self):
        return self._brake.value

    @brake.setter
    def brake(self, var):
        self._brake.value = var

    @property
    def friction(self):
        return self._friction.value

    @friction.setter
    def friction(self, var):
        self._friction.value = var

    @property
    def damping(self):
        return self._damping.value

    @damping.setter
    def damping(self, var):
        self._damping.value = var

    @property
    def spring_stiffness(self):
        return self._spring_stiffness.value

    @spring_stiffness.setter
    def spring_stiffness(self, var):
        self._spring_stiffness.value = var

    @property
    def torque(self):
        return self._torque.value

    @torque.setter
    def torque(self, var):
        self._torque.value = var

    @property
    def measured_torque(self):
        return self._measured_torque.value

    @measured_torque.setter
    def measured_torque(self, var):
        self._measured_torque.value = var

    @property
    def endstops(self):
        return self._endstops.value

    @endstops.setter
    def endstops(self, var):
        self._endstops.value = var

    @property
    def torque_limit_between_endstops(self):
        return self._torque_limit_between_endstops.value

    @torque_limit_between_endstops.setter
    def torque_limit_between_endstops(self, var):
        self._torque_limit_between_endstops.value = var

    @property
    def torque_limit_beyond_endstops(self):
        return self._torque_limit_beyond_endstops.value

    @torque_limit_beyond_endstops.setter
    def torque_limit_beyond_endstops(self, var):
        self._torque_limit_beyond_endstops.value = var

    @property
    def sensodrive_motorstate(self):
        return self._sensodrive_motorstate.value

    @sensodrive_motorstate.setter
    def sensodrive_motorstate(self, var):
        self._sensodrive_motorstate.value = var

    @property
    def sensodrive_ID(self):
        return self._sensodrive_ID.value
    @sensodrive_ID.setter
    def sensodrive_ID(self, var):
        self._sensodrive_ID.value = var