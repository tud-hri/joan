from .states import States
from .statehandler import StateHandler

class HapticTrainer():
    '''
    Make this 1 unique instance with state and statehandler

    ?? Enter new states per module in here ??
    '''
    __instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.__instance:
            klass.__instance = object.__new__(HapticTrainer)
            print('new instance of HapticTrainer')
        return klass.__instance

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.statehandler = StateHandler()
        self.states = States()
        self.gui = 'gui' in kwargs.keys() and kwargs['gui'] or None                       
        print ("init")

    def result(self):
        return (self.args, self.kwargs)

if __name__ == '__main__':
    print ('Deprecated, see process directory')
    exit(0)
    from statehandler import StateHandler
    from states import States
    try:
        h1 = HapticTrainer(23,6, e='1')
        print (h1, h1.result())

        h2 = HapticTrainer(32,9, e="2")
        print (h2, h2.result())
        assert h1 == h2, "no singleton"

        
        print (h2.statehandler.state)
        #statehandler= StateHandler()
        states = States()
        print (h2.statehandler.requestStateChange(states.ERROR))
        print (h2.statehandler.requestStateChange(states.EXPERIMENT))
    except Exception as inst:
        print (inst)