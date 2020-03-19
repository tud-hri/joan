from process import State, MasterStates, translate

class FeedbackcontrollerStates(MasterStates):
    # states
    FEEDBACKCONTROLLER                   = State(700, translate('FeedbackcontrollerState', 'Feedbackcontroller State'), -1,150)
    

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in FeedbackcontrollerStates', state, self.states[state])
       
    
