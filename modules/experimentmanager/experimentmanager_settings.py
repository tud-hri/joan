from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class ExperimentManagerSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.EXPERIMENT_MANAGER)

    def reset(self):
        pass
