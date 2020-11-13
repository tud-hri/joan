import os

from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from core.statesenum import State


class DatarecorderMPManager(ModuleManager):
    """ Manages the datarecordermp environment """

    def __init__(self, news, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.DATA_RECORDER, news=news, time_step_in_ms=time_step_in_ms, parent=parent)

        self.state_machine.set_exit_action(State.INITIALIZED, self.module_dialog.apply_settings)
        self.state_machine.set_transition_condition(State.INITIALIZED, State.READY, self._check_save_path)

    def _check_save_path(self):
        # save current settings
        self.module_dialog.apply_settings()

        if not bool(os.path.dirname(self.module_settings.path_to_save_file)):
            return False, "No save path was provided."
        elif not os.path.isdir(os.path.dirname(self.module_settings.path_to_save_file)):
            return False, "Directory of save path does not exist."
        else:
            return True
