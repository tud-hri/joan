from process import State, MasterStates, translate

class SiminterfaceStates(MasterStates):
    # SensoDrive states
    SIMULATION                    = State(400, translate('SiminterfaceState', 'Siminterface State'), -1,150)
    SIMULATION.INITIALIZING       = State(401, translate('SiminterfaceState', 'Simulation Initializing'), -1,150,404,405)
    SIMULATION.RUNNING            = State(402, translate('SiminterfaceState', 'Simulation Running'), -1,150,404,403) 
    SIMULATION.STOPPED            = State(403, translate('SiminterfaceState', 'Simulation Stopped'), -1,150,404,402)
    SIMULATION.ERROR              = State(404, translate('SiminterfaceState', 'Simulation Error'), -1,150,406)
    SIMULATION.ERROR.INIT         = State(405, translate('SiminterfaceState', 'Simulation Error'), -1,150,406)
    SIMULATION.ERROR.CLEARED      = State(406, translate('SiminterfaceState', 'Simulation Error'), -1,150,400)
    

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in SiminterfacecontrollerStates', state, self.states[state])
       

