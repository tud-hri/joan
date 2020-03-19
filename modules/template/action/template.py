from process import Control

class TemplateAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__
        # get state information from module Widget
        self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or {}
        self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None
