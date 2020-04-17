"""
StateHandler

This object is the center for all application state related changes. 
It contains the application state. It handles requests of state changes (from other objects) 
and emits a signal when the state has changed to all object which are listening/connected.
This approach is slightly different from the lopes app, where the interface with the 
HLC is the 'boss' of the state (i.e. other classes request the interface for changes)
"""

from PyQt5 import QtCore
from .states import State, MasterStates
#import ctypes

class StateHandler(QtCore.QObject):
    """
    """

    # signals  
    state_changed = QtCore.pyqtSignal(int)

    # properties
    @property
    def state(self):
        """Property: get the current state"""
        return self._state

    # Methods
    def __init__(self, *args, **kwargs):
        """ Initialize StateHandler. """
        QtCore.QObject.__init__(self)

        self._state = 'first_state' in kwargs.keys() and kwargs['first_state'] or MasterStates.VOID
        self.states = 'states_dict' in kwargs.keys() and kwargs['states_dict'] or {}

    def get_state(self, no):
        """Given a state number (as an int), it returns the state object.
        Raises a KeyError if no state with the given number exists.
        If a state itself is given (i.e., an object of type State, it is
        returned immediately."""
        if isinstance(no, State):
            return no
        elif isinstance(no, int):
            try:
                return self.states[no]
            except KeyError:
                # Raise a key error with better description
                raise KeyError("No state with number %d" % no)
        else:
            raise TypeError("variable 'no' should be an int (or State).")

    def request_state_change(self, requested_state):
        """ Process requests for state change from outside """
        # check if the state transition is allowed

        if self.is_state_transition_allowed(self._state, requested_state):
            self._set_state(requested_state)
        else:
            raise RuntimeError('State change not allowed.')

    def allowed_transitions(self, current_state):
        """ Return allowed state transitions for current state. """
        state = current_state

        allowed_transitions = state.transitions

        allowed_transitions += (int(state),)  # change to the same state is also allowed

        while state.parent:
            allowed_transitions += state.parent.transitions
            state = state.parent

        return allowed_transitions

    def is_state_transition_allowed(self, currentstate, requested_state):
        """ Return true/false if state transition is allowed """
        allowed_transitions = self.allowed_transitions(currentstate)

        return (requested_state in allowed_transitions) or (-1 in allowed_transitions)

    def _set_state(self, s):
        """ Set the current state. """
        self._state = s

        # state is changed, emit signal to other objects
        self.state_changed.emit(int(self._state))

    def get_current_state(self):
        return self._state
