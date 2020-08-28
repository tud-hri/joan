from process.joanmodulesettings import JoanModuleSettings
from modules.joanmodules import JOANModules


class ScenarioSettings(JoanModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.SCENARIOS)

        self.current_scenario = None
