from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import TemplateStates


class TemplateAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=100, callbacks=None):
        super().__init__(module=JOANModules.TEMPLATE, master_state_handler=master_state_handler, millis=millis, callbacks=callbacks)

        self.moduleStateHandler.requestStateChange(TemplateStates.TEMPLATE.READY)

    def start(self):
        if super().start():
            self.moduleStateHandler.requestStateChange(TemplateStates.TEMPLATE.RUNNING)
            return True
        return False

    def stop(self):
        if super().stop():
            self.moduleStateHandler.requestStateChange(TemplateStates.TEMPLATE.STOPPED)
            return True
        return False
