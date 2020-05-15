""" Definition of the state machine

Overview
--------
The GUI is always in a certain state.

"""

from PyQt5 import QtCore
translate = QtCore.QCoreApplication.translate


class State:
    """ State(nr, name, \*transitions)
    
    State object that contains lots of nice information about a state:
    * nr: the integer state number, can be obtaine by calling int() on the object.
    * parent: the integer state number for the parent state
    * name: a short description of the state
    * key: the uppercase name by which the state is stored in the MasterStates class and in the module_states class
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


class MasterStates:
    instance = None
    """ 
    The MasterStates collection class should only contain the global singleton MasterStates
    Each module has its own module_states that inherits this global MasterStates class
    """
    
    # void state. The program starts in VOID
    VOID                            = State(0, translate('BootStates', 'Null state'), -1, 150, 101)
    
    # Idle states
    IDLE                            = State(100, translate('IdleStates', 'Idle mode'), -1, 150)
    
    # Initialize
    INITIALIZING                    = State(110, translate('InitStates', 'Systems initializing'), -1, 150)
    INITIALIZED                     = State(111, translate('InitStates', 'Systems initialized'), -1, 150)

    # Error state
    ERROR                           = State(150, translate('ErrorStates', 'Error'), 100, 110)

    # Emergengy stop
    EMERGENCY                       = State(101, translate('EmergencyStates', 'Emergency stop'), -1, 999)

    QUIT                            = State(999, translate('Quit', 'Quit'), -1)

    def __init__(self):
        # Dict of integers to state objects, filled in during __init__
        self.states = {}
        
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
                    if state.nr in self.states:
                        raise RuntimeError('Duplicate state: ', state.nr)
                    self.states[state.nr] = state
                    # Look into state
                    tagStates(state, '%s%s.' % (baseKey, key))
        
        # Tag whole tree
        tagStates(self, '')
    
    def get_states(self):
        return self.states
