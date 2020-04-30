from process import State, MasterStates, translate

class CarlainterfaceStates(MasterStates):
    # SensoDrive states
    SIMULATION                    = State(400, translate('CarlainterfaceState', 'Carlainterface State'), -1,150)
    SIMULATION.INITIALIZING       = State(401, translate('CarlainterfaceState', 'Carlaulation Initializing'), -1,150,404,405)
    SIMULATION.RUNNING            = State(402, translate('CarlainterfaceState', 'Carlaulation Running'), -1,150,404,403) 
    SIMULATION.STOPPED            = State(403, translate('CarlainterfaceState', 'Carlaulation Stopped'), -1,150,404,402)
    SIMULATION.ERROR              = State(404, translate('CarlainterfaceState', 'Carlaulation Error'), -1,150,406)
    SIMULATION.ERROR.INIT         = State(405, translate('CarlainterfaceState', 'Carlaulation Error'), -1,150,406)
    SIMULATION.ERROR.CLEARED      = State(406, translate('CarlainterfaceState', 'Carlaulation Error'), -1,150,400)
    
    

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in CarlainterfacecontrollerStates', state, self.states[state])
       

