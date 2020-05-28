from modules.joanmodules import JOANModules
from process.joanmodulesettings import JoanModuleSettings


class DataRecorderSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        super().__init__(module_enum)

        self.variables_to_save = {}

        for module in JOANModules:
            self.variables_to_save[module.name] = {}
