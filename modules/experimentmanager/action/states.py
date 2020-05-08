from process import State, MasterStates, translate


class ExperimentManagerStates(MasterStates):
    # SensoDrive states
    EXPERIMENTMANAGER = State(200, translate('ExperimentManagerState', 'ExperimentManager State'), -1, 150)
    EXPERIMENTMANAGER.STOPPED = State(201, translate('ExperimentManagerState', 'ExperimentManager Off'), -1, 150, 202, 204, 205)
    EXPERIMENTMANAGER.READY = State(202, translate('ExperimentManagerState', 'ExperimentManager Ready'), -1, 150, 201, 203, 204)
    EXPERIMENTMANAGER.RUNNING = State(203, translate('ExperimentManagerState', 'ExperimentManager On'), -1, 150, 202, 204)
    EXPERIMENTMANAGER.ERROR = State(204, translate('ExperimentManagerState', 'ExperimentManager Error'), -1, 150, 201)
    EXPERIMENTMANAGER.ERROR.INIT = State(205, translate('ExperimentManagerState', 'ExperimentManager Initialization Error'), -1, 150, 201)
    EXPERIMENTMANAGER.INITIALIZED = State(206, translate('ExperimentManagerState', 'ExperimentManager Initialized'),
                                            -1, 150, 201, 202, 203, 204, 205)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self)