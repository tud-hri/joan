from process import State, MasterStates, translate

class InterfaceStates(MasterStates):
    # SensoDrive states
    TEMPLATE                   = State(900, translate('TemplateState', 'Template State'), -1,150)


    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in TemplateStates', state, self.states[state])
       
    
