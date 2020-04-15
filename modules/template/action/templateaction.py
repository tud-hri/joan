from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import TemplateStates


class TemplateAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=100):
        super().__init__(module=JOANModules.TEMPLATE, master_state_handler=master_state_handler, millis=millis)

        self.moduleStateHandler.requestStateChange(TemplateStates.TEMPLATE.READY)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        pass

    def initialize(self):
        """
        This function is called before the module is started
        """
        pass

    def start(self):
        try:
            self.moduleStateHandler.requestStateChange(TemplateStates.TEMPLATE.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.moduleStateHandler.requestStateChange(TemplateStates.TEMPLATE.STOPPED)
        except RuntimeError:
            return False
        return super().start()
