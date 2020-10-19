import platform
import sys

import multiprocessing as mp
import time

from core.statesenum import State
from modules.joanmodules import JOANModules
from core.exceptionhook import exception_log_and_kill_hook

if platform.system() == 'Windows':
    import wres


class ModuleProcess(mp.Process):
    def __init__(self, module: JOANModules, time_step_in_ms, news, start_event):
        super().__init__()

        if time_step_in_ms < 10:
            raise ValueError('The time step of a JOAN process cannot be smaller then 10 ms (not > 100 Hz). This is not possible on a non real time OS.')

        self.module = module
        self._time_step_in_ns = time_step_in_ms * 1e6
        self._time = 0.0

        self._start_event = start_event

        # print(news.all_news)
        self._sharedvalues_module = news.read_news(module)

    def get_ready(self):
        pass

    def do_function(self):
        pass

    def run(self):
        """
        Run function, starts once process.start is called.
        Note: anything you created in __init__ needs to be picklable. If not, create the non-picklable objects in the function get_ready
        :return:
        """
        try:
            self.get_ready()
            self._start_event.wait()

            # run
            if platform.system() == 'Windows':
                with wres.set_resolution(10000):
                    self._run_loop()
            else:
                self._run_loop()
        except:
            # sys.excepthook is not called from within processes so can't be overridden. instead, catch all exceptions here and call the new excepthook manually
            exception_log_and_kill_hook(*sys.exc_info(), self.module)

    def _run_loop(self):

        running = True
        while running:
            t0 = time.perf_counter_ns()

            self._time = time.perf_counter_ns()

            self.read_from_shared_values()

            self.do_function()

            self.write_to_shared_values()

            if self._sharedvalues_module.state == State.STOPPED.value:
                running = False

            execution_time = time.perf_counter_ns() - t0

            time.sleep((self._time_step_in_ns - execution_time) * 1e-9)

    def read_from_shared_values(self):
        """
        Read all needed values from shared and copy them to local values here.
        This should be done here only; before executing the do function
        :return:
        """
        pass

    def write_to_shared_values(self):
        """
        Write to shared values. This should only happen in this function!
        :return:
        """
        self._sharedvalues_module.time = self._time
