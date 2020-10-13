import multiprocessing as mp
import time

from modules.joanmodules import JOANModules


class ModuleProcess(mp.Process):

    def __init__(self, module: JOANModules, time_step, news):
        super().__init__()
        self._time_step = time_step

        self._state = news[module].state

    def do(self):
        pass

    def run(self):
        t_start = time.perf_counter_ns()
        t_prev = t_start

        running = True
        while running:
            t = time.perf_counter_ns() * 1e-9
            if t - t_prev >= self._time_step:
                self.do()
                t_prev = t

            # for now, stop after 5 sec
            if t > 5.0:
                running = False
