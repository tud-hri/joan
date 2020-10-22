import multiprocessing as mp

from PyQt5 import QtCore

from core.statemachine import StateMachine
from core.statesenum import State


class ModuleExceptionMonitor(QtCore.QThread):
    def __init__(self, exception_event: mp.Event, state_machine: StateMachine):
        super().__init__()

        self.exception_event = exception_event
        self.state_machine = state_machine

        self.start()

    def run(self):
        while True:
            self.exception_event.wait()
            self.state_machine.request_state_change(State.ERROR)
            self.exception_event.clear()
