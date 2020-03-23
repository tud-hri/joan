from process import State, MasterStates, translate

class DatarecorderStates(MasterStates):
    # Datarecorder states
    DATARECORDER                    = State(200, translate('Data Recorder', 'Data Recorder'), -1)
    DATARECORDER.NOTINITIALIZED     = State(210, translate('Data Recorder', 'Not initialized'), -1)
    DATARECORDER.INITIALIZING       = State(220, translate('Data Recorder', 'Initializing'), -1)
    DATARECORDER.INITIALIZED        = State(230, translate('Data Recorder', 'Initialized'), -1)
    DATARECORDER.START              = State(240, translate('Data Recorder', 'Data Recorder started'), -1)
    DATARECORDER.STOP               = State(250, translate('Data Recorder', 'Data Recorder stopped'), -1)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in TemplateStates', state, self.states[state])
       
    
