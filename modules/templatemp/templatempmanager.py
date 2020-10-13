
import os

from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from core.modulemanager import ModuleManager
from core.statesenum import State


class TemplateMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step=0.01):
        super().__init__(module=JOANModules.TEMPLATE_MP, time_step=time_step)

    def initialize(self):
        print("init")
        return super().initialize()

    def start(self):
        print("start")
        return super().start()

    def stop(self):
        return super().stop()
