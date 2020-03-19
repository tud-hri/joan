from process import State, MasterStates, translate

class TemplateStates(MasterStates):
    # SensoDrive states
    TEMPLATE                   = State(200, translate('TemplateState', 'Template State'), -1,150)
    TEMPLATE.OFF               = State(201, translate('TemplateState', 'Template Off'), -1,150, 202, 204,2040)
    TEMPLATE.READY             = State(202, translate('TemplateState', 'Template Ready'), -1,150, 201, 203,204)
    TEMPLATE.ON                = State(203, translate('TemplateState', 'Template On'), -1,150, 202, 204)
    TEMPLATE.ERROR             = State(204, translate('TemplateState', 'Template Error'), -1, 150, 201)
    TEMPLATE.ERROR.INIT        = State(2040, translate('TemplateState', 'Template Initialization Error'), -1, 150, 201)
    TEMPLATE.INITIALIZED       = State(205, translate('TemplateState', 'Template Initialized'), -1, 150, 201, 202, 203, 204,2040)

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in TemplateStates', state, self.states[state])
       
    
