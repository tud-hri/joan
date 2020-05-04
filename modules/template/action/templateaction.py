from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import TemplateStates


class TemplateAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=100):
        super().__init__(module=JOANModules.TEMPLATE, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(TemplateStates.TEMPLATE.READY)

        self.data = {}
        self.data['t'] = 0
        self.write_news(news=self.data)
        self.time = QtCore.QTime()

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        self.data['t'] = self.time.elapsed()
        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        pass

    def start(self):
        try:
            self.module_state_handler.request_state_change(TemplateStates.TEMPLATE.RUNNING)
            self.time.restart()
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(TemplateStates.TEMPLATE.STOPPED)
        except RuntimeError:
            return False
        return super().stop()
