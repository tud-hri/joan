from process import State, MasterStates, translate

class SiminterfaceStates(MasterStates):
    # SensoDrive states
    SIMINTERFACECONTROLLER                   = State(400, translate('SiminterfacecontrollerState', 'Siminterfacecontroller State'), -1,150)
    

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in SiminterfacecontrollerStates', state, self.states[state])
       
    
