""" Definition of the state machine

Overview
--------
The GUI is always in a certain state.

"""


#from util import QtCore#, translate
from PyQt5 import QtCore
translate = QtCore.QCoreApplication.translate
#import time

class State:
    """ State(nr, name, \*transitions)
    
    State object that contains lots of nice information about a state:
    * nr: the integer state number, can be obtaine by calling int() on the object.
    * parent: the integer state number for the parent state
    * name: a short description of the state
    * key: the uppercase name by which the state is stored in the States class
    * transitions: tuple of possible state transitions
    
    """
    
    def __init__(self, nr, name, *transitions):
        self.parent = None # Set later
        self.key = None # Set later
        self.nr = int(nr)
        self.name = str(name)
        self.transitions = tuple(transitions)
    
    def __int__(self):
        return int(self.nr)
    
    def __contains__(self, state):
        """ Returns true if s is a child state. For convenience, this state is
        contained by itself, so that `s in STATE.X` returns true if s happens to
        be STATES.X. 
        """
        
        myStates = States()
        if type(state) is int:
            state = myStates.states[state]
            #state = STATES.states[state]
        
        state = str(state)
        return state in myStates.getChildren(self.key) + [self.key]
        #return state in STATES.getChildren(self.key) + [self.key]
    
    def __eq__(self, other):
        return self.nr == int(other)
    
    def __ne__(self, other):
        return self.nr != int(other)
    
    def __hash__(self):
        return self.nr
    
    def __str__(self):
        return self.key
        
    def __repr__(self):
        return '<State "%s" (%i)>' % (self.key, self.nr)


class States:
    """ States collection class. """
    
    # void state. The program starts in VOID
    VOID                            = State(0, translate('BootStates', 'Null state'), -1,150)
    
    # Idle states
    IDLE                            = State(100, translate('IdleStates', 'Idle mode'), -1,150)
    
    # Initialize
    INITIALIZING                    = State(110, translate('InitStates', 'System initializing'), -1,150)
    INITIALIZED                     = State(111, translate('InitStates', 'System initialized'), -1,150)
    INITIALIZED.INTERFACE           = State(112, translate('InitStates', 'Interface initialized'), -1,150)
    INITIALIZED.DATARECORDER        = State(113, translate('InitStates', 'Datarecorder initialized'), -1,112)
    
    # Experiment running states
    EXPERIMENT                      = State(130, translate('ExperimentState', 'Experiment mode'), -1,150)
    EXPERIMENT.TRIAL                = State(131, translate('ExperimentState', 'Experiment-trial mode'), -1,150)
    EXPERIMENT.TRIAL.READY          = State(132, translate('ExperimentState', 'Experiment-trial mode'), -1, 150)
    EXPERIMENT.TRIAL.GOTO           = State(133, translate('ExperimentState', 'Experiment-trial goto'), -1, 150)
    EXPERIMENT.TRIAL.COUNTDOWN      = State(134, translate('ExperimentState', 'Experiment-trial countdown'), -1, 150)
    EXPERIMENT.TRIAL.TASK           = State(135, translate('ExperimentState', 'Experiment-trial task'), -1, 150)
    EXPERIMENT.BREAK                = State(137, translate('ExperimentState', 'Experiment break'), -1, 150)
    EXPERIMENT.PAUSED               = State(138, translate('ExperimentState', 'Experiment paused'), -1, 150)
    EXPERIMENT.SUBJECTIDENTERED     = State(139, translate('ExperimentState', 'Experiment subject ID entered'), -1, 150)
    EXPERIMENT.WAITING              = State(1310, translate('ExperimentState', 'Experiment waiting'), -1, 150)

    # SensoDrive states
    STEERINGWHEEL                   = State(200, translate('SteeringwheelState', 'Steering wheel State'), -1,150)
    STEERINGWHEEL.OFF               = State(201, translate('SteeringwheelState', 'Steeringwheel Off'), -1,150, 202, 204)
    STEERINGWHEEL.READY             = State(202, translate('SteeringwheelState', 'Steeringwheel Ready'), -1,150, 201, 203,204)
    STEERINGWHEEL.ON                = State(203, translate('SteeringwheelState', 'Steeringwheel On'), -1,150, 202, 204)
    STEERINGWHEEL.ERROR             = State(204, translate('SteeringwheelState', 'Steeringhweel Error'), -1, 150, 201)
    STEERINGWHEEL.INITIALIZED       = State(205, translate('SteeringwheelState', 'Steeringhweel Error'), -1, 150, 201, 202, 203, 204)



    # Debug / developing
    DEBUG                           = State(140, translate('DebugStates', 'Debugging'), -1)
    DEBUG.DATARECORDER              = State(141, translate('DebugStates', 'Debugging - Datarecorder'), -1)
    DEBUG.DATARECORDER.START        = State(142, translate('DebugStates', 'Debugging - Datarecorder started'), -1)

    # Exceptions
    ERROR                           = State(150,  translate('ErrorStates', 'Error'), 100,110)
    ERROR.INTERFACE                 = State(151,  translate('ErrorStates', 'Error - Interface initialization'), 100,111,151)
    ERROR.INTERFACE.INIT_NIDAQ      = State(152,  translate('ErrorStates', 'Error - Interface initialization, NIDAQ'), 100,111,151,153,154)
    ERROR.INTERFACE.INIT_SIMENDO    = State(153,  translate('ErrorStates', 'Error - Interface initialization, SIMENDO'), 100,111,151,152,154)
    ERROR.INTERFACE.INIT_DEV        = State(154,  translate('ErrorStates', 'Error - Interface initialization, DEV'), 100,111,151,152,153)
    ERROR.EXPERIMENT                = State(155,  translate('ErrorStates', 'Error - Experiment'), -1, 150)
    

    '''
    States is only used by SingletonControl
    __instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.__instance:
            klass.__instance = object.__new__(States)
            print('new instance of States')
        return klass.__instance
    '''

    # Dict of integers to state objects, filled in during __init__
    states = {}
    
    def __init__(self):
        # Get states and clear just to be sure
        states = self.states
        states.clear()
        
        def tagStates(baseState, baseKey):
            #print(baseKey, baseState)
            for key in dir(baseState):
                if key.upper() == key and not key.startswith('_'):
                    state = getattr(baseState, key)
                    if not isinstance(state, State):
                        raise RuntimeError('Invalid state: ' + repr(state))
                    # Set state
                    state.key = baseKey + key
                    if baseState is self:
                        state.parent = None
                    else:
                        state.parent = baseState
                    # Store state number
                    if state.nr in states:
                        raise RuntimeError('Duplicate state: ', state.nr)
                    states[state.nr] = state
                    # Look into state
                    tagStates(state, '%s%s.' % (baseKey, key))
        
        # Tag whole tree
        tagStates(self, '')
    
    
    def untagState(self, key):
        """ Returns a state object for a given key. """
        
        chain = key.split(".")
        
        state = self
        for substate in chain:
            state = getattr(state, substate)
        
        return state
    
    def getChildren(self, key):
        """ Returns a list of child states, or an empty list.
        
        If the state has no children, an empty list is returned. Otherwise, a
        list of substates is retured, in the format STATE.SUBSTATE. The list is
        built recursively, so it also returns children of children.
        """
        
        children = list()
        for attr in dir(self.untagState(key)):
            if attr.upper() == attr and not attr.startswith('_'):
                child = "%s.%s" % (key, attr)
                children.append(child)
                children += self.getChildren(child)
        
        return children

    def getChildrenAsState(self,state):
        """ See getChildren(). This function returns a list of states instead
        of a list of tags. Also, the input is a state, not a key.
        """
        return [self.untagState(s) for s in self.getChildren(state.key)]

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

# STATES object as singleton state collection
#STATES = States()


# class StateProxy(QtCore.QObject):
#     """ StateProxy(model)
#     
#     Proxy class to set and get the state of the HLC model. It continuously polls
#     the model on the xPC target and emits a signal when the state has changed.
#     
#     Parameters
#     ----------
#     model : Model
#         Instance of :py:class:`xpc.Model`
#     args : list
#         Arguments to be passed on to the base class constructor
#     kwargs : dict
#         Keyword arguments to be passed on to the base class constructor
#     """
#     
#     
#     # Signals
#     stateChanged = QtCore.Signal(object) # (newState)
#     
#     # Time-out value for state transitions
#     ST_TIMEOUT = 1  # in seconds
#     
#     def __init__(self, model, *args, **kwargs):
#         QtCore.QObject.__init__(self, *args, **kwargs)
#         
#         # Store model and initial state
#         self._model = model
#         self._latestState = STATES.VOID
#         self._timer = None
#         self._halt = False
#     
#     def start(self):
#         """ Start polling by creating a new timer. """
#         
#         # Kill any existing timer
#         if self._timer:
#             self.killTimer(self._timer)
#         
#         # Create timer object
#         self._timer = self.startTimer(200)
#         if not self._timer:
#             raise RuntimerError("Could not create timer")
#     
#     
#     def stop(self):
#         """ Interrupt polling. """
#         
#         # Set halt flag
#         if self._timer:
#             self._halt = True
#     
#     
#     def requestStateChange(self, s):
#         """ requestState(s)
#         
#         Request the state to be changed to a new state. The given value can be
#         a State instance or an int.
#         
#         """
#         s = int(s)
#         
#         # Make sure that the request state is zero
#         if self._model.StateChangeRequest.p.Value != 0:
#             self._model.StateChangeRequest.p.Value = 0
#             t = time.time()
#             while self._model.StateChangeRequest.s[0] != 0:
#                 # Test for time-out
#                 if time.time() - t > self.ST_TIMEOUT:
#                     raise RuntimeError("State machine reports nonzero request state; timed out while waiting")
#                     break
#                 else:
#                     time.sleep(0.001)
#         
#         # Set the actual requested state
#         self._model.StateChangeRequest.p.Value = s
#         
#         # Wait for the signal to become the requested value
#         t = time.time()
#         while self._model.StateChangeRequest.s[0] != s:
#             if time.time() - t > self.ST_TIMEOUT:
#                 raise RuntimeError("State machine is not transitioning to desired state; timed out while waiting")
#                 break
#             else:
#                 time.sleep(0.001)
#         
#         # Set requested state to zero
#         self._model.StateChangeRequest.p.Value = 0
#     
#     
#     def currentState(self):
#         """ currentState()
#         
#         Return the State object corresponding to the current state.
#         The state object can be converted to an int.
#         
#         """
#         self._poll()
#         return self._latestState
#     
#     
#     def isActiveState(self, value):
#         """ isActiveState(value)
#         
#         Check if the given state is currently active. A state is also
#         active if one of its child states is active. The given value
#         can be a State instance or an int.
#         
#         """
#         self._poll()
#         value = int(value)
#         
#         # Check if the current state is the one asked about
#         state = self._latestState
#         if int(state) == value:
#             return True
#         
#         # Check if any of the children are active
#         for child in STATES.getChildren(state.key):
#             if STATES.untagState(child) == value:
#                 return True
#             else:
#                 return False
#     
#     
#     def allowedTransitions(self):
#         """ Return allowed state transitions for current state. """
#         state = self._latestState
#         allowed_transitions = state.transitions
#         while state.parent:
#             allowed_transitions += state.parent.transitions
#             state = state.parent
#         
#         return allowed_transitions
#     
#     
#     def timerEvent(self, event):
#         """ Catches timer events. """
#         
#         # Check if we are still asked to poll the model.
#         if event.timerId() == self._timer:
#             if self._halt:
#                 self.killTimer(self._timer)
#             else:
#                 self._poll()
#     
#     
#     def _poll(self):
#         """ _poll()
#         
#         This method should be called to get the latest state.
#         
#         """
#         
#         # Prevent recursion on an error
#         if self._latestState == STATES.CONNECTION_ERROR:
#             return self._latestState
#         
#         try:
#             nr = self._model.StateMachine.s[0,0]
#         except Exception:
#             #print('An Exception occured while polling the state. Stopping poll timer...')
#             #self.killTimer(self._timer)
#             #raise # reraise; the error message will be shown once
#             print('An Exception occured while polling the state.')
#             self._latestState = STATES.CONNECTION_ERROR
#             self.stateChanged.emit(self._latestState)
#             
#         else:
#             # Check for state change
#             if nr != int(self._latestState):
#                 self._latestState = STATES.states.get(int(nr), STATES.VOID)
#                 self.stateChanged.emit(self._latestState)
#         
#         return self._latestState



if __name__ == '__main__':
    pass
