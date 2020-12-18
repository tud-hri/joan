from core.module_manager import ModuleManager
from core.statesenum import State
from modules.joanmodules import JOANModules


class DataPlotterManager(ModuleManager):
    """ Manages the datarecorder environment """

    def __init__(self, news, central_settings, signals, central_state_monitor, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.DATA_PLOTTER, news=news, central_settings=central_settings, signals=signals,
                         central_state_monitor=central_state_monitor, time_step_in_ms=time_step_in_ms, parent=parent)

        self.state_machine.set_exit_action(State.INITIALIZED, self.module_dialog.apply_settings)
