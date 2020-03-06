from process import Control

class InterfaceWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 20
        kwargs['callback'] = [self.do]  # method will run each given millis

        kwargs['ui'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),"template.ui")
        Control.__init__(self, *args, **kwargs)

        self.statehandler.stateChanged.connect(self.handlestate)

        pass