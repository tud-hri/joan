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
    
    ## signals
    #stateChanged = QtCore.Signal(int) #: Signal(int), emitted when the Lopes state has changed
    stateChanged = QtCore.pyqtSignal(int)
    
    ## properties
    @property
    def state(self):
        """Property: get the current state"""
        return self._state


    '''
    @property   
    def state_c_int(self):
        return self._state_c_int

    @property
    def state_pointer(self):
        return self._state_pointer
    '''

    ## Methods
    def __init__(self, *args, **kwargs):
    #def __init__(self, haptictrainer, *args, **kwargs):
        """ Initialize StateHandler. """
        QtCore.QObject.__init__(self)
        #self._haptictrainer = haptictrainer # keep a reference to haptic trainer (our umbrella)
        
        # MasterStates (there is a MasterStates class and each module has its own ModuleStates)
        #self._state = MasterStates.VOID
        #self.states = MasterStates.states   # TODO voor moduleStates via arguments
        self._state = 'firstState' in kwargs.keys() and kwargs['firstState'] or MasterStates.VOID
        self.states = 'statesDict' in kwargs.keys() and kwargs['statesDict'] or {}

        #self._state_c_int = ctypes.c_int(int(self._state))
        #self._state_pointer = ctypes.addressof(self._state_c_int)

    def getState(self,no):
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
                raise KeyError("No state with number %d"%no)
        else:
            raise TypeError("variable 'no' should be an int (or State).")

    def requestStateChange(self, requestedstate):
        """ Process requests for state change from outside """
        # check if the change of state is allowed 
        # (check for the allowed transitions)
        
        if self.isStateTransitionAllowed(self._state, requestedstate):
        #if self.myStates.isStateTransitionAllowed(self._state, requestedstate):
        #if STATES.isStateTransitionAllowed(self._state, requestedstate):
            self._setState(requestedstate)
        else:
            raise RuntimeError('State change not allowed.')
        
    def allowedTransitions(self, currentstate):
        """ Return allowed state transitions for current state. """
        state = currentstate
        
        allowed_transitions = state.transitions
        
        allowed_transitions += (int(state),) # change to the same state is also allowed
        
        while state.parent:
            allowed_transitions += state.parent.transitions
            state = state.parent

        return allowed_transitions
        
    def isStateTransitionAllowed(self, currentstate, requestedstate):
        """ Return true/false if state transition is allowed """
        
        allowed_transitions = self.allowedTransitions(currentstate)

        if (requestedstate in allowed_transitions) or (-1 in allowed_transitions):
            return True
        else:
            return False


    def _setState(self, s):
        """ Set the current state. """
        self._state = s
        #self._state_c_int.value = int(self._state)

        # state is changed, emit signal to other objects
        self.stateChanged.emit(int(self._state))

    def getCurrentState(self):
        return self._state
