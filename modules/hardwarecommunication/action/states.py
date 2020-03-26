from process import State, MasterStates, translate

class HardwarecommunicationStates(MasterStates):
    # SensoDrive states
    HARDWARECOMMUNICATION                   = State(200, translate('HardwarecommunicationState', 'Hardwarecommunication State'), -1,150)
    HARDWARECOMMUNICATION.STOPPED           = State(201, translate('HardwarecommunicationState', 'Hardwarecommunication Off'), -1,150, 202, 204,2040)
    HARDWARECOMMUNICATION.READY             = State(202, translate('HardwarecommunicationState', 'Hardwarecommunication Ready'), -1,150, 201, 203,204)
    HARDWARECOMMUNICATION.RUNNING           = State(203, translate('HardwarecommunicationState', 'Hardwarecommunication On'), -1,150, 202, 204)
    HARDWARECOMMUNICATION.ERROR             = State(204, translate('HardwarecommunicationState', 'Hardwarecommunication Error'), -1, 150, 201)
    HARDWARECOMMUNICATION.ERROR.INIT        = State(2040, translate('HardwarecommunicationState', 'Hardwarecommunication Initialization Error'), -1, 150, 201)
    HARDWARECOMMUNICATION.INITIALIZED       = State(205, translate('HardwarecommunicationState', 'Hardwarecommunication Initialized'), -1, 150, 201, 202, 203, 204,2040)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in HardwarecommunicationStates', state, self.states[state])
       
    
