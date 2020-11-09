from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules
from pathlib import Path
from datetime import datetime


class DatarecorderMPSettings(ModuleSettings):
    def __init__(self):
        super().__init__(module=JOANModules.DATARECORDER_MP)

        '''
        if Path(module_manager.settings_filename).is_file():
            self.load_from_file(self.module_manager.settings_filename)
        else:
            self.time_step = 20  # set default if self.time_step does not exist
            self.save_to_file(self.module_manager.settings_filename)
        '''