from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class DatarecorderSettings(ModuleSettings):
    def __init__(self):
        super().__init__(module=JOANModules.DATA_RECORDER)

        self.path_to_save_file = ''
        self.variables_to_be_saved = []