"""
StateHandler

This object is the center for all application state related changes. 
It contains the application state. It handles requests of state changes (from other objects) 
and emits a signal when the state has changed to all object which are listening/connected.
This approach is slightly different from the lopes app, where the interface with the 
HLC is the 'boss' of the state (i.e. other classes request the interface for changes)
"""

from PyQt5 import QtCore
from states import State, States
import ctypes

class StateHandler(QtCore.QObject):
    """
    """
    
    ## signals
    stateChanged = QtCore.Signal(int) #: Signal(int), emitted when the Lopes state has changed
    
    ## properties
    @property
    def state(self):
        """Property: get the current state"""
        return self._state

    @property   
    def state_c_int(self):
        return self._state_c_int

    @property
    def state_pointer(self):
        return self._state_pointer

    ## Methods
    def __init__(self, *args, **kwargs):
    #def __init__(self, haptictrainer, *args, **kwargs):
        """ Initialize StateHandler. """
        QtCore.QObject.__init__(self, *args, **kwargs)
        #self._haptictrainer = haptictrainer # keep a reference to haptic trainer (our umbrella)
        
        myStates = States()
        self._state = myStates.VOID
        #self._state = STATES.VOID
        self._state_c_int = ctypes.c_int(int(self._state))
        self._state_pointer = ctypes.addressof(self._state_c_int)
        
    def requestStateChange(self, requestedstate):
        """ Process requests for state change from outside """
        # check if the change of state is allowed 
        # (check for the allowed transitions)
        
        myStates = States()
        if myStates.isStateTransitionAllowed(self._state, requestedstate):
        #if STATES.isStateTransitionAllowed(self._state, requestedstate):
            self._setState(requestedstate)
        else:
            raise RuntimeError('State change not allowed.')
        
    def _setState(self, s):
        """ Set the current state. """
        self._state = s
        self._state_c_int.value = int(self._state)

        # state is changed, emit signal to other objects
        self.stateChanged.emit(int(self._state))
