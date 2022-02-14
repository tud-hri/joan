from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class DataRecorderSettings(ModuleSettings):
    def __init__(self):
        super().__init__(module=JOANModules.DATA_RECORDER)

        self.path_to_save_file = ''
        self.append_timestamp_to_filename = True
        self.variables_to_be_saved = []

        self.path_to_trajectory_save_file = ''
        self.should_record_trajectory = False

    def reset(self):
        self.path_to_save_file = ''
        self.variables_to_be_saved = []
        self.path_to_trajectory_save_file = ''
        self.should_record_trajectory = False
