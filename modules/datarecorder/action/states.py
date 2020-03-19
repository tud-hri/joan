from process import State, MasterStates, translate

class DatarecorderStates(MasterStates):
    # SensoDrive states
    DEBUG                           = State(140, translate('DebugStates', 'Debugging'), -1)
    DEBUG.DATARECORDER              = State(141, translate('DebugStates', 'Debugging - Datarecorder'), -1)
    DEBUG.DATARECORDER.START        = State(142, translate('DebugStates', 'Debugging - Datarecorder started'), -1)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in TemplateStates', state, self.states[state])
       
    
