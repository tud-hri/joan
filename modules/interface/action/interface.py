from process import Control

class InterfaceAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self,*args, **kwargs)
        self.moduleStates = None
        self.moduleStateHandler = None
        try:
            statePackage = self.getModuleStatePackages(module='module.interface.widget.interface.InterfaceWidget')
            self.moduleStates = statePackage['moduleStates']
            self.moduleStateHandler = statePackage['moduleStateHandler']
        except:
            pass
