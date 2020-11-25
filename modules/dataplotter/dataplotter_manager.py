import os

from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from core.statesenum import State


class DataPlotterManager(ModuleManager):
    """ Manages the datarecorder environment """

    def __init__(self, news, signals, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.DATA_PLOTTER, news=news, signals=signals, time_step_in_ms=time_step_in_ms, parent=parent)

        self.state_machine.set_exit_action(State.INITIALIZED, self.module_dialog.apply_settings)