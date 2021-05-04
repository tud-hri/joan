import abc
import multiprocessing as mp
import platform
import sys
import time

from core.exceptionhook import exception_log_and_kill_hook
from core.statesenum import State
from modules.joanmodules import JOANModules

if platform.system() == 'Windows':
    import wres


class ProcessEvents:
    """
    Class containing all events for communication between module_process and module_manager
    """

    def __init__(self):
        self.start = mp.Event()
        self.exception = mp.Event()
        self.process_is_ready = mp.Event()
        self.emergency = mp.Event()


class ModuleProcess(mp.Process):
    """
    Base class for the module process.
    """

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events: ProcessEvents, settings_singleton):
        super().__init__(daemon=True)

        if time_step_in_ms < 10:
            raise ValueError('The time step of a JOAN process cannot be smaller then 10 ms (not > 100 Hz). This is not possible on a non real time OS.')

        self.module = module
        self._time_step_in_ns = time_step_in_ms * 1e6
        self._time = 0.0
        self._last_t0 = 0.0
        self._last_execution_time = 0.0
        self._running_frequency = 0.0

        self._settings_as_dict = settings.as_dict()
        self._settings_as_object = None

        # extract shared variables from news
        self._module_shared_variables = news.read_news(module)
        # extract settings from singleton settings
        self.singleton_settings = settings_singleton

        # mp.Events
        self._events = events

    def _get_ready(self):
        # settings dict back to settings object
        self._settings_as_object = self.module.settings()  # create empty settings object
        self._settings_as_object.load_from_dict(self._settings_as_dict)  # settings as object

        # get_ready to
        self.get_ready()

        self._events.process_is_ready.set()

    @abc.abstractmethod
    def get_ready(self):
        """
        get_ready is called when the module goes to READY state. This function is called from the new process (in run()).
        :return:
        """

    @abc.abstractmethod
    def do_while_running(self):
        """
        User-defined function, in which the user's desired operations occur every loop cycle.
        :return:
        """
        pass

    def run(self):
        """
        Run function, starts once start() is called.
        Note: anything you created in __init__ and you want to use in run() needs to be picklable. Failing the 'picklable' requirement will result in errors.
        If you need to use an object from __init__ that is not picklable, see if you can translate your object into something
        picklable (lists, dicts, primitives etc) and create a new object in here. Example: settings in get_ready.
        :return:
        """
        try:
            self._get_ready()

            self._events.start.wait()

            # run
            if platform.system() == 'Windows':
                with wres.set_resolution(10000):
                    self._run_loop()

            else:
                self._run_loop()
        except:
            # sys.excepthook is not called from within processes so can't be overridden. instead, catch all exceptions here and call the new excepthook manually
            exception_log_and_kill_hook(*sys.exc_info(), self.module, self._events.exception)

    def _run_loop(self):
        """
        The run loop, which attempts to run at a desired frequency (through time.sleep).
        Keeps track of time.
        Shared variables should only be read or written to once per loop tick (e.g. read shared variables, store in local variables, and write to sv
        :return:
        :return:
        """
        running = True

        # check if state is stopped; if so, stop!
        if self._module_shared_variables.state == State.STOPPED.value:
            running = False

        t_start = time.perf_counter_ns()

        while running:

            # check if state is stopped; if so, stop!
            if self._module_shared_variables.state == State.STOPPED.value:
                running = False

            t0 = time.perf_counter_ns()

            try:
                self._running_frequency = 1e9 / (t0 - self._last_t0)
            except ZeroDivisionError:
                self._running_frequency = 1e9 / 1.

            self._last_t0 = t0
            self._time = time.time_ns() - t_start

            # read shared values here, store in local variables
            self.read_from_shared_variables()

            # do_while_running!
            self.do_while_running()

            # write local variables to shared values
            self.write_to_shared_variables()

            # check if state is stopped; if so, stop!
            if self._module_shared_variables.state == State.STOPPED.value:
                running = False

            self._last_execution_time = time.perf_counter_ns() - t0

            # sleep for time step, taking the execution time into account
            if (self._time_step_in_ns - self._last_execution_time) * 1e-9 > 0:
                time.sleep((self._time_step_in_ns - self._last_execution_time) * 1e-9)

    def close_down(self):
        pass

    def read_from_shared_variables(self):
        """
        Read all needed values from shared and copy them to local variables.
        This should be done here only; before executing the do_while_running function
        :return:
        """
        pass

    def write_to_shared_variables(self):
        """
        Write to shared values from your local variables. This should only happen in this function!
        :return:
        """
        self._module_shared_variables.running_frequency = self._running_frequency
        self._module_shared_variables.execution_time = self._last_execution_time
        self._module_shared_variables.time = self._time
