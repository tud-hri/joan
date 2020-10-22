import multiprocessing as mp

from PyQt5 import QtCore

from core.statemachine import StateMachine
from core.statesenum import State


class ModuleExceptionMonitor(QtCore.QThread):
    """
    Exception monitor that transitions modules to ERROR state when uncaught exception occurs (in process).
    Creates a threads which blocks until an exception event is set.
    """
    def __init__(self, exception_event: mp.Event, state_machine: StateMachine):
        """
        init
        :param exception_event: event from process that exception occured
        :param state_machine: module statemachine
        """
        super().__init__()

        self.exception_event = exception_event
        self.state_machine = state_machine

        self.start()

    def run(self):
        """
        Thread's run function, blocks, waits for exception event, sets statemachine to ERROR, clears the event and keeps monitoring.
        :return:
        """
        while True:
            self.exception_event.wait()
            self.state_machine.request_state_change(State.ERROR)
            self.exception_event.clear()
