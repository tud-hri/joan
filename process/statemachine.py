from .statesenum import State
from modules.joanmodules import JOANModules


class StateMachine:
    def __init__(self, module_enum: JOANModules):
        self.current_state = State.IDLE
        self.state_message = ''

        self._module_enum = module_enum

        self._transition_conditions = {}

        for departing_state in State:
            self._transition_conditions[departing_state] = {}

            for target_state in State:
                if departing_state is not target_state:
                    self._transition_conditions[departing_state][target_state] = lambda: True

        self._entry_actions = {}
        self._exit_actions = {}

        for state in State:
            self._entry_actions[state] = None
            self._exit_actions[state] = None

    def request_state_change(self, target_state, state_message_on_success=''):
        if self._transition_conditions[self.current_state][target_state]():
            if self._exit_actions[self.current_state]:
                self._exit_actions[self.current_state]()

            self.current_state = target_state
            self.state_message = state_message_on_success

            if self._entry_actions[target_state]:
                self._entry_actions[target_state]()
        else:
            self.state_message = 'State change from ' + self.current_state + ' to ' + target_state + ' is illegal for ' + self._module_enum + ' module.'
            self.current_state = State.ERROR
