from enum import Enum


class State(Enum):
    ERROR = -1
    STOPPED = 0
    INITIALIZED = 1
    READY = 2
    RUNNING = 3

    def __str__(self):
        return {State.ERROR: 'Error',
                State.STOPPED: 'Stopped',
                State.INITIALIZED: 'Initialized',
                State.READY: 'Ready',
                State.RUNNING: 'Running'}[self]
