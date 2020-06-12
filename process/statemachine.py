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

        # declare state changes that are illegal by default
        self._transition_conditions[State.IDLE][State.RUNNING] = lambda: False
        self._transition_conditions[State.RUNNING][State.READY] = lambda: False
        self._transition_conditions[State.ERROR][State.READY] = lambda: False
        self._transition_conditions[State.ERROR][State.RUNNING] = lambda: False

        self._entry_actions = {}
        self._exit_actions = {}

        for state in State:
            self._entry_actions[state] = None
            self._exit_actions[state] = None

    def set_transition_condition(self, departing_state: State, target_state: State, condition_function: callable):
        """
        Method for setting a transition condition for a specific state change. The callable condition is evaluated when the state change is requested. If it
        returns True the state change is accepted. If it returns false, the state change is rejected and the state will be set to error. In this case an error
        message can also be returned to specify why the state change is illegal.

        :param departing_state: the state before the transition
        :param target_state: the state after the transition
        :param condition_function: a callable condition that should return True when state change is legal, could also return an error message
        :return:
        """
        if departing_state is target_state:
            raise ValueError('State machine cannot only transition conditions for transitioning between two different states.')

        self._transition_conditions[departing_state][target_state] = condition_function

    def set_exit_action(self, state: State, action: callable):
        self._exit_actions[state] = action

    def set_entry_action(self, state: State, action: callable):
        self._entry_actions[state] = action

    def request_state_change(self, target_state, state_message_on_success=''):
        condition_evaluation = self._transition_conditions[self.current_state][target_state]()

        if len(condition_evaluation) == 1:
            state_change_is_legal = condition_evaluation
            error_message = ''
        else:
            state_change_is_legal, error_message = condition_evaluation

        if state_change_is_legal:
            if self._exit_actions[self.current_state]:
                self._exit_actions[self.current_state]()

            self.current_state = target_state
            self.state_message = state_message_on_success

            if self._entry_actions[target_state]:
                self._entry_actions[target_state]()
        else:
            self.state_message = 'State change from ' + self.current_state + ' to ' + target_state + ' is illegal for ' + self._module_enum + ' module. '
            if error_message:
                self.state_message += 'Error: ' + error_message
            self.current_state = State.ERROR
