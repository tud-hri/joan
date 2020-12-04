from modules.joanmodules import JOANModules
from .statesenum import State


class StateMachine:
    def __init__(self, module_enum: JOANModules = None):
        self.current_state = State.STOPPED
        self.state_message = ''

        self._module_enum = module_enum

        self._transition_conditions = {}

        for departing_state in State:
            self._transition_conditions[departing_state] = {}

            for target_state in State:
                if departing_state is not target_state:
                    self._transition_conditions[departing_state][target_state] = lambda: True

        # declare state changes that are illegal by default
        # allowed state order: STOPPED -> INITIALIZED -> READY -> RUNNING -> STOPPED
        # from any state, allow transition to STOPPED
        self._transition_conditions[State.STOPPED][State.READY] = lambda: False
        self._transition_conditions[State.STOPPED][State.RUNNING] = lambda: False
        self._transition_conditions[State.INITIALIZED][State.RUNNING] = lambda: False
        self._transition_conditions[State.READY][State.INITIALIZED] = lambda: False
        self._transition_conditions[State.RUNNING][State.READY] = lambda: False
        self._transition_conditions[State.RUNNING][State.INITIALIZED] = lambda: False

        # error only to stopped
        self._transition_conditions[State.ERROR][State.INITIALIZED] = lambda: False
        self._transition_conditions[State.ERROR][State.READY] = lambda: False
        self._transition_conditions[State.ERROR][State.RUNNING] = lambda: False

        self._entry_actions = {}
        self._exit_actions = {}
        self._automatic_transitions = {}

        for state in State:
            self._entry_actions[state] = None
            self._exit_actions[state] = None
            self._automatic_transitions[state] = None

        self._state_change_listeners = []

    def add_state_change_listener(self, listener: callable):
        """
        Register listeners by supplying a callable method. This function will be called on every state change.
        :param listener: (callable) method to be executed when the state changes
        :return: None
        """
        if listener not in self._state_change_listeners:
            self._state_change_listeners.append(listener)

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
            raise ValueError(
                'State machine cannot only transition conditions for transitioning between two different states.')

        self._transition_conditions[departing_state][target_state] = condition_function

    def set_automatic_transition(self, departing_state: State, target_state: State):
        """
        Method to set an automatic transition from a state to a next state. Every state can have one possible automatic transition, which is executed subject
        to the normal conditions after the departing state is entered. Note that the departing state is not skipped, it is fully entered and exited like
        normally, but it is done automatically.

        :param departing_state: (State) The state which should be automatically left when entered if the transition to the target state is immediately legal
        :param target_state: (State) The state to automatically move to
        :return: None
        """
        if departing_state is State.ERROR:
            raise ValueError('Automatic transitioning out of the error state is disabled for safety reasons.')

        self._automatic_transitions[departing_state] = target_state

    def set_exit_action(self, state: State, action: callable):
        """
        Set an exit action for a state. This action is called every time the state is departed.
        :param state: (State) State for which the action should be executed
        :param action: (callable) The method to be called when the state is departed
        :return: None
        """
        self._exit_actions[state] = action

    def set_entry_action(self, state: State, action: callable):
        """
        Set an entry action for a state. This action is called every time the state is entered.
        :param state: (State) State for which the action should be executed
        :param action: (callable) The method to be called when the state is entered
        :return: None
        """
        self._entry_actions[state] = action

    def request_state_change(self, target_state, state_message_on_success=''):
        """
        Request a state change, check if allowed, and execute the registered exit/entry/transition functions
        :param target_state: target state
        :param state_message_on_success: optional message
        :return:
        """
        if target_state is not self.current_state:
            condition_evaluation = self._transition_conditions[self.current_state][target_state]()

            if isinstance(condition_evaluation, bool):
                state_change_is_legal = condition_evaluation
                error_message = ''
            elif isinstance(condition_evaluation, tuple) and len(condition_evaluation) == 2:
                state_change_is_legal, error_message = condition_evaluation
            else:
                raise RuntimeError(
                    "A transition condition function should return a boolean indicating if a transition is legal. Or a tuple containing a "
                    "boolean and a (error) message to display. Received object was of type: " + str(type(condition_evaluation)))

            if state_change_is_legal:
                if self._exit_actions[self.current_state]:
                    self._exit_actions[self.current_state]()

                self.current_state = target_state
                self.state_message = state_message_on_success

                if self._entry_actions[target_state]:
                    self._entry_actions[target_state]()
            else:
                self.state_message = 'State change from ' + str(self.current_state) + ' to ' + str(
                    target_state) + ' is illegal for ' + str(self._module_enum) + ' module. Will remain in current state'
                if error_message:
                    self.state_message += 'Error: ' + error_message

            for listener in self._state_change_listeners:
                listener()

            if self._automatic_transitions[self.current_state]:
                automatic_target_state = self._automatic_transitions[self.current_state]
                condition_evaluation = self._transition_conditions[self.current_state][automatic_target_state]()

                if isinstance(condition_evaluation, bool):
                    state_change_is_legal = condition_evaluation
                else:
                    state_change_is_legal, _ = condition_evaluation

                if state_change_is_legal:
                    self.request_state_change(automatic_target_state)
