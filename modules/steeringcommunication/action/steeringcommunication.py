from process import Control
from modules.steeringcommunication.action.PCANBasic import *

class SteeringcommunicationAction(Control):
    def __init__(self, *args, **kwargs):
        kwargs['ui'] = None
        Control.__init__(self,*args, **kwargs)

            
    
    def initialize(self):
        print('Initializing...')
        try:
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.INITIALIZED)
            self.ready()
        except:
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.ERROR)


    def ready(self):
        if(self.statehandler._state is self.states.STEERINGWHEEL.INITIALIZED):
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.READY)

    def start(self):
        print('Pressed Start')
        if(self.statehandler._state is self.states.STEERINGWHEEL.READY):
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.ON)

    def stop(self):
        print('Pressed Stop')
        if(self.statehandler._state is self.states.STEERINGWHEEL.ON):
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.READY)
