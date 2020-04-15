from process import Control


class TemplateAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.moduleStates = None
        self.moduleStateHandler = None

        try:
            statePackage = self.getModuleStatePackage(module='modules.template.widget.template.TemplateWidget')
            self.moduleStates = statePackage['moduleStates']
            self.moduleStateHandler = statePackage['moduleStateHandler']
        except Exception as inst:
            print('Exception in TemplateAction', inst)
