
from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from core.module_manager import ModuleManager
from core.statesenum import State


class TemplateMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step=1, parent=None):
        super().__init__(module=JOANModules.TEMPLATE_MP, time_step=time_step, parent=parent)

    def initialize(self):
        print("init")
        return super().initialize()

    def start(self):
        print("start")
        return super().start()

    def stop(self):
        print("stop")
        return super().stop()
