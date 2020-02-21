
from states import States

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
        self.states = States()
        print ("init")

    def result(self):
        return (self.args, self.kwargs)

if __name__ == '__main__':
    try:
        h1 = HapticTrainer(23,6, e='1')
        print (h1, h1.result())

        h2 = HapticTrainer(32,9, e="2")
        print (h2, h2.result())
        assert h1 == h2, "no singleton"

        print (h2.states.getState(150))
    except Exception as inst:
        print (inst)