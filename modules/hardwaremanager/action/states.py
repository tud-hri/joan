from process import State, MasterStates, translate

class HardwaremanagerStates(MasterStates):
    # Hardware manager states
    #Idle
    IDLE                          = State(100, translate('Hardwaremanager State', 'Hardwaremanager Idle'), -1,150)

    #Initialization States
    INIT                          = State(200, translate('Hardwaremanager State', 'Hardwaremanager Init'), -1,150)
    INIT.INITIALIZING             = State(201, translate('Hardwaremanager State', 'Hardwaremanager Initializing'), -1, 400)
    INIT.INITIALIZED              = State(202, translate('Hardwaremanager State', 'Hardwaremanager Initialized'), -1,150)

    #Execution States
    EXEC                          = State(300, translate('Hardwaremanager State', 'Hardwaremanager Exec'), -1, 150,400)
    EXEC.READY                    = State(301, translate('Hardwaremanager State', 'Hardwaremanager Ready'), -1, 150,400)
    EXEC.RUNNING                  = State(302, translate('Hardwaremanager State', 'Hardwaremanager Running'), -1, 150,400)
    EXEC.STOPPED                  = State(303, translate('Hardwaremanager State', 'Hardwaremanager Stopped'), -1, 150,400)

    #Error States
    ERROR                         = State(400, translate('Hardwaremanager State', 'Hardwaremanager Error'), -1,150,100)
    ERROR.INIT                    = State(401, translate('Hardwaremanager State', 'Hardwaremanager Initialization Error'), -1,150,100)
    ERROR.EXEC                    = State(402, translate('Hardwaremanager State', 'Hardwaremanager Execution Error'), -1,150,100)
    ERROR.OTHER                   = State(403, translate('Hardwaremanager State', 'Hardwaremanager Other Error'), -1,150,100)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in HardwarecommunicationStates', state, self.states[state])
       
    
