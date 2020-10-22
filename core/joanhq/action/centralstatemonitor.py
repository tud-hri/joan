from core.statemachine import StateMachine
from core.statesenum import State
from modules.joanmodules import JOANModules


class CentralStateMonitor:
    def __init__(self):
        self._all_state_machines = {}

    def register_state_machine(self, module: JOANModules, state_machine: StateMachine):
        state_machine.add_state_change_listener(lambda: self._state_changed(module, state_machine))
        self._all_state_machines[module] = state_machine

    def _state_changed(self, module: JOANModules, state_machine: StateMachine):
        new_state = state_machine.current_state

        if new_state == State.ERROR:
            for other_module, other_state_machine in self._all_state_machines.items():
                if other_module != module:
                    other_state_machine.request_state_change(State.STOPPED)
