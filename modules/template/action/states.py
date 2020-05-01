from process import State, MasterStates, translate


class TemplateStates(MasterStates):
    # Template States
    #Idle
    IDLE                          = State(100, translate('Template State', 'Template Idle'), -1,150)

    #Initialization States
    INIT                          = State(200, translate('Template State', 'Template Init'), -1,150)
    INIT.INITIALIZING             = State(201, translate('Template State', 'Template Initializing'), -1, 400)
    INIT.INITIALIZED              = State(202, translate('Template State', 'Template Initialized'), -1,150)

    #Execution States
    EXEC                          = State(300, translate('Template State', 'Template Exec'), -1, 150,400)
    EXEC.READY                    = State(301, translate('Template State', 'Template Ready'), -1, 150,400)
    EXEC.RUNNING                  = State(302, translate('Template State', 'Template Running'), -1, 150,400)
    EXEC.STOPPED                  = State(303, translate('Template State', 'Template Stopped'), -1, 150,400)

    #Error States
    ERROR                         = State(400, translate('Template State', 'Template Error'), -1,150,100)
    ERROR.INIT                    = State(401, translate('Template State', 'Template Initialization Error'), -1,150,100)
    ERROR.EXEC                    = State(402, translate('Template State', 'Template Execution Error'), -1,150,100)
    ERROR.OTHER                   = State(403, translate('Template State', 'Template Other Error'), -1,150,100)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self)
