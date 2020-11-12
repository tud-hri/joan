from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class DatarecorderMPManager(ModuleManager):
    """ Manages the datarecordermp environment """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.DATA_RECORDER, time_step_in_ms=time_step_in_ms, parent=parent)
        # TODO: implement transition condition that only allows transitioning to run if a valid save path has been set

    def get_ready(self):
        self.module_dialog.apply_settings()
        super().get_ready()
