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


class ModuleProcess(mp.Process):
    """
    Base class for the module process.
    """

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event, exception_event, process_is_ready_event):
        super().__init__()

        if time_step_in_ms < 10:
            raise ValueError('The time step of a JOAN process cannot be smaller then 10 ms (not > 100 Hz). This is not possible on a non real time OS.')

        self.module = module
        self._time_step_in_ns = time_step_in_ms * 1e6
        self._time = 0.0

        self._settings_as_dict = settings.as_dict()
        self._settings_as_object = None

        # extract shared variables from news
        self._module_shared_variables = news.read_news(module)

        # mp.Events
        self._start_event = start_event
        self._exception_event = exception_event
        self._process_is_ready_event = process_is_ready_event

    def _get_ready(self):
        # settings dict back to settings object
        self._settings_as_object = self.module.settings()  # create empty settings object
        self._settings_as_object.load_from_dict(self._settings_as_dict)  # settings as object

        # get_ready to
        self.get_ready()

        self._process_is_ready_event.set()

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
            self._start_event.wait()

            # run
            if platform.system() == 'Windows':
                with wres.set_resolution(10000):
                    self._run_loop()
            else:
                self._run_loop()
        except:
            # sys.excepthook is not called from within processes so can't be overridden. instead, catch all exceptions here and call the new excepthook manually
            exception_log_and_kill_hook(*sys.exc_info(), self.module, self._exception_event)

    def _run_loop(self):
        """
        The run loop, which attempts to run at a desired frequency (through time.sleep).
        Keeps track of time.
        Shared variables should only be read or written to once per loop tick (e.g. read shared variables, store in local variables, and write to sv
        :return:
        """
        running = True
        while running:
            t0 = time.perf_counter_ns()

            self._time = time.perf_counter_ns()

            # read shared values here, store in local variables
            self.read_from_shared_variables()

            # do_while_running!
            self.do_while_running()

            # write local variables to shared values
            self.write_to_shared_variables()

            # check if state is stopped; if so, stop!
            if self._module_shared_variables.state == State.STOPPED.value:
                running = False

            execution_time = time.perf_counter_ns() - t0

            # sleep for time step, taking the execution time into account
            time.sleep((self._time_step_in_ns - execution_time) * 1e-9)

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
        self._module_shared_variables.time = self._time
