from process import State, MasterStates, translate

class SteeringcommunicationStates(MasterStates):
    # SensoDrive states
    STEERINGWHEEL                   = State(200, translate('SteeringwheelState', 'Steering wheel State'), -1,150)
    STEERINGWHEEL.OFF               = State(201, translate('SteeringwheelState', 'Steeringwheel Off'), -1,150, 202, 204,2040)
    STEERINGWHEEL.READY             = State(202, translate('SteeringwheelState', 'Steeringwheel Ready'), -1,150, 201, 203,204)
    STEERINGWHEEL.ON                = State(203, translate('SteeringwheelState', 'Steeringwheel On'), -1,150, 202, 204)
    STEERINGWHEEL.ERROR             = State(204, translate('SteeringwheelState', 'Steeringwheel Error'), -1, 150, 201)
    STEERINGWHEEL.ERROR.INIT        = State(2040, translate('SteeringwheelState', 'Steeringwheel Initialization Error'), -1, 150, 201)
    STEERINGWHEEL.INITIALIZED       = State(205, translate('SteeringwheelState', 'Steeringwheel Initialized'), -1, 150, 201, 202, 203, 204,2040)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in TemplateStates', state, self.states[state])
       
    
