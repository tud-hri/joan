from process import Control

class HardwarecommunicationAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.moduleStates = None
        self.moduleStateHandler = None
        try:
            statePackage = self.getModuleStatePackage(module='module.hardwarecommunication.widget.Hardwarecommunication.TemplateWidget')
            self.moduleStates = statePackage['moduleStates']
            self.moduleStateHandler = statePackage['moduleStateHandler']
        except Exception as inst:
            print(inst)
