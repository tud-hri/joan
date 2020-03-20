from process import State, MasterStates, translate

class TrajectoryrecorderStates(MasterStates):
    # SensoDrive states
    TRAJECTORYGENERATOR                  = State(500, translate('TemplateState', 'Template State'), -1,150)
 
    

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in TemplateStates', state, self.states[state])
       
    
