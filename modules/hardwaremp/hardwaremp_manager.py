
import os

from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from core.module_manager import ModuleManager
from core.statesenum import State


class HardwareMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step=1, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, time_step=time_step, parent=parent)


    def initialize(self):
        return super().initialize()

    def start(self):
        return super().start()

    def stop(self):
        return super().stop()

    def add_hardware(self):
        print('joe')
