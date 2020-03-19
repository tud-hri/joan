from process import State, MasterStates, translate

class InterfaceStates(MasterStates):
    # SensoDrive states
    INTERFACE                   = State(900, translate('SteeringwheelState', 'Steering wheel State'), -1,150)
    INTERFACE.OFF               = State(901, translate('SteeringwheelState', 'Steeringwheel Off'), -1,150, 902)
    INTERFACE.READY             = State(902, translate('SteeringwheelState', 'Steeringwheel Ready'), -1,150, 901, 903)
    INTERFACE.ON                = State(903, translate('SteeringwheelState', 'Steeringwheel On'), -1,150, 902)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in TemplateStates', state, self.states[state])
       
    
