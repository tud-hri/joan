from process import Control

class Manualcontrol(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self,*args, **kwargs)
        print('News', self.getAllNews())

class FDCAcontrol(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self,*args, **kwargs)
        print('News', self.getAllNews())
    

    