from process import State, MasterStates, translate

class SteeringWheelControlStates(MasterStates):
    # states
    # Idle
    IDLE                          = State(100, translate('SteeringWheelControl State', 'SteeringWheelControl Idle'), -1,150)

    # Initialization States
    INIT                          = State(200, translate('SteeringWheelControl State', 'SteeringWheelControl Init'), -1,150)
    INIT.INITIALIZING             = State(201, translate('SteeringWheelControl State', 'SteeringWheelControl Initializing'), -1, 400)
    INIT.INITIALIZED              = State(202, translate('SteeringWheelControl State', 'SteeringWheelControl Initialized'), -1,150)

    # Execution States
    EXEC                          = State(300, translate('SteeringWheelControl State', 'SteeringWheelControl Exec'), -1, 150,400)
    EXEC.READY                    = State(301, translate('SteeringWheelControl State', 'SteeringWheelControl Ready'), -1, 150,400)
    EXEC.RUNNING                  = State(302, translate('SteeringWheelControl State', 'SteeringWheelControl Running'), -1, 150,400)
    EXEC.STOPPED                  = State(303, translate('SteeringWheelControl State', 'SteeringWheelControl Stopped'), -1, 150,400)

    # Error States
    ERROR                         = State(400, translate('SteeringWheelControl State', 'SteeringWheelControl Error'), -1,150,100)
    ERROR.INIT                    = State(401, translate('SteeringWheelControl State', 'SteeringWheelControl Initialization Error'), -1,150,100)
    ERROR.EXEC                    = State(402, translate('SteeringWheelControl State', 'SteeringWheelControl Execution Error'), -1,150,100)
    ERROR.OTHER                   = State(403, translate('SteeringWheelControl State', 'SteeringWheelControl Other Error'), -1,150,100)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self)  
