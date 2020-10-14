from enum import Enum


class State(Enum):
    ERROR = -1
    IDLE = 0
    PREPARED = 1
    READY = 2
    RUNNING = 3
    STOPPED = 4

    def __str__(self):
        return {State.ERROR: 'Error',
                State.IDLE: 'Idle',
                State.PREPARED: 'Prepared',
                State.READY: 'Ready',
                State.RUNNING: 'Running',
                State.STOPPED: 'Clean-up'}[self]
