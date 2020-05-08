from process import State, MasterStates, translate

class CarlainterfaceStates(MasterStates):
    # Carla Interface States
    #Idle
    IDLE                          = State(100, translate('CarlainterfaceState', 'Carla Interface Idle'), -1,150)

    #Initialization States
    INIT                          = State(200, translate('CarlainterfaceState', 'Carla Interface Init'), -1,150)
    INIT.INITIALIZING             = State(201, translate('CarlainterfaceState', 'Carla Interface Initializing'), -1, 400)
    INIT.INITIALIZED              = State(202, translate('CarlainterfaceState', 'Carla Interface Initialized'), -1,150)

    #Execution States
    EXEC                          = State(300, translate('CarlainterfaceState', 'Carla Interface Exec'), -1, 150,400)
    EXEC.READY                    = State(301, translate('CarlainterfaceState', 'Carla Interface Ready'), -1, 150,400)
    EXEC.RUNNING                  = State(302, translate('CarlainterfaceState', 'Carla Interface  Running'), -1, 150,400)
    EXEC.STOPPED                  = State(303, translate('CarlainterfaceState', 'Carla Interface Stopped'), -1, 150,400)

    #Error States
    ERROR                         = State(400, translate('CarlainterfaceState', 'Carla Interface Error'), -1,150,100)
    ERROR.INIT                    = State(401, translate('CarlainterfaceState', 'Carla Interface Initialization Error'), -1,150,100)
    ERROR.EXEC                    = State(402, translate('CarlainterfaceState', 'Carla Interface Execution Error'), -1,150,100)
    ERROR.OTHER                   = State(403, translate('CarlainterfaceState', 'Carla Interface Other Error'), -1,150,100)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in CarlainterfacecontrollerStates', state, self.states[state])
       

