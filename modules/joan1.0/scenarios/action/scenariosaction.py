from core.joanmoduleaction import JoanModuleAction
from core.statesenum import State
from modules.joanmodules import JOANModules
from .scenariossettings import ScenarioSettings


class ScenariosAction(JoanModuleAction):
    def __init__(self, millis=100, enable_performance_monitor=True):
        super().__init__(JOANModules.SCENARIOS, millis, enable_performance_monitor)
        self.settings = ScenarioSettings()

        self.share_settings(self.settings)

    def do(self):
        if self.settings.current_scenario is not None:
            self.settings.current_scenario.do_function(self)

    def initialize(self):
        self.state_machine.request_state_change(State.READY)

    def start(self):
        self.state_machine.request_state_change(State.RUNNING)
        super().start()

    def stop(self):
        self.state_machine.request_state_change(State.INITIALIZED)
        super().stop()
