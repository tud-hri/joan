import os

from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from core.statesenum import State


class DataRecorderManager(ModuleManager):
    """
    Manages the datarecorder environment
    """

    def __init__(self, news, central_settings, signals, time_step_in_ms=10, parent=None):
        """
        :param news: dict with all the news (shared variable) objects of other modules
        :param signals: dict with signals for inter-module communication
        :param time_step_in_ms:
        :param parent:
        """
        super().__init__(module=JOANModules.DATA_RECORDER, news=news, central_settings=central_settings, signals=signals, time_step_in_ms=time_step_in_ms,
                         parent=parent)

        self.state_machine.set_exit_action(State.INITIALIZED, self.module_dialog.apply_settings)
        self.state_machine.set_transition_condition(State.INITIALIZED, State.READY, self._check_save_path)

    def _check_save_path(self):
        if not bool(os.path.dirname(self.module_settings.path_to_save_file)):
            return False, "No save path was provided."
        elif not os.path.isdir(os.path.dirname(self.module_settings.path_to_save_file)):
            return False, "Directory of save path does not exist."
        else:
            return True
