from enum import Enum


class State(Enum):
    ERROR = -1
    IDLE = 0
    READY = 1
    RUNNING = 2

    def __str__(self):
        return {State.ERROR: 'Error',
                State.IDLE: 'Idle',
                State.READY: 'Ready',
                State.RUNNING: 'Running'}[self]
