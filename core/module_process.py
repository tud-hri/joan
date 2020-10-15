import multiprocessing as mp
import time

from core.statesenum import State
from modules.joanmodules import JOANModules


class ModuleProcess(mp.Process):

    def __init__(self, module: JOANModules, time_step, news):
        super().__init__()
        self.module = module
        self._time_step = time_step
        self._time = 0.0

        # print(news.all_news)
        self._sharedvalues_module = news.read_news(module)

    def do_function(self):
        pass

    def run(self):
        # prepare for loop: efficiency? Does this pin the CPU?
        t_start = time.perf_counter_ns() * 1e-9
        t_prev = t_start

        running = True
        while running:
            t = time.perf_counter_ns() * 1e-9
            if t - t_prev >= self._time_step:
                self.do_function()

                self._time = t - t_start

                self.write_to_shared_values()
                t_prev = t

            # stop if module STOP
            if self._sharedvalues_module.state == State.STOP.value:
                running = False

        print("Stopped process:", self.module)

    def write_to_shared_values(self):
        """
        Write to shared values. This should only happen in this function!
        :return:
        """
        self._sharedvalues_module.time = self._time
