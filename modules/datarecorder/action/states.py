from process import State, MasterStates, translate


class DatarecorderStates(MasterStates):
    # States taken from other modules
    #Idle
    IDLE                          = State(100, translate('Data Recorder', 'Data Recorder Idle'), -1, 150)

    #Initialization States
    INIT                          = State(200, translate('Data Recorder', 'Data Recorder Init'), -1, 150)
    INIT.INITIALIZING             = State(201, translate('Data Recorder', 'Data Recorder Initializing'), -1, 400)
    INIT.INITIALIZED              = State(202, translate('Data Recorder', 'Data Recorder Initialized'), -1, 150)

    #Execution States
    EXEC                          = State(300, translate('Data Recorder', 'Data Recorder Exec'), -1, 150,400)
    EXEC.READY                    = State(301, translate('Data Recorder', 'Data Recorder Ready'), -1, 150,400)
    EXEC.RUNNING                  = State(302, translate('Data Recorder', 'Data Recorder  Running'), -1, 150,400)
    EXEC.STOPPED                  = State(303, translate('Data Recorder', 'Data Recorder Stopped'), -1, 150,400)

    # original states (renumbered to the 500-range)
    # Datarecorder states
    DATARECORDER = State(500, translate('Data Recorder', 'Data Recorder'), -1)
    DATARECORDER.NOTINITIALIZED = State(510, translate('Data Recorder', 'Not initialized'), -1)
    DATARECORDER.INITIALIZING = State(520, translate('Data Recorder', 'Initializing'), -1)
    DATARECORDER.INITIALIZED = State(530, translate('Data Recorder', 'Initialized'), -1)
    DATARECORDER.START = State(540, translate('Data Recorder', 'Data Recorder started'), -1)
    DATARECORDER.STOP = State(550, translate('Data Recorder', 'Data Recorder stopped'), -1)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self)
