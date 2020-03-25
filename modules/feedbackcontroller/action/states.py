from process import State, MasterStates, translate

class FeedbackcontrollerStates(MasterStates):
    # states
    FEEDBACKCONTROLLER                   = State(700, translate('FeedbackcontrollerState', 'Feedbackcontroller State'), -1,150)
    FEEDBACKCONTROLLER.RUNNING           = State(701, translate('FeedbackcontrollerState', 'Feedbackcontroller Running'), -1,150,703,702)
    FEEDBACKCONTROLLER.STOPPED           = State(702, translate('FeedbackcontrollerState', 'Feedbackcontroller Stopped'), -1,150,703,701)
    FEEDBACKCONTROLLER.ERROR             = State(703, translate('FeedbackcontrollerState', 'Feedbackcontroller Error'), -1,150,701)
    

    def __init__(self, *args, **kwargs):
        MasterStates.__init__(self) 

        #for state in self.states:
        #    print('in FeedbackcontrollerStates', state, self.states[state])
       
    
