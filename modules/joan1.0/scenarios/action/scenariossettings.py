from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules
from modules.scenarios.scenarios.scenarioslist import ScenariosList


class ScenarioSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.SCENARIOS)

        self.current_scenario = None

    def reset(self):
        self.current_scenario = None

    def as_dict(self):
        dict_to_return = super(ScenarioSettings, self).as_dict()

        if self.current_scenario is not None:
            dict_to_return[str(self._module_enum)]['current_scenario'] = self.current_scenario.name
        return dict_to_return

    def set_from_loaded_dict(self, loaded_dict):
        self.reset()
        super(ScenarioSettings, self).set_from_loaded_dict(loaded_dict)
        if loaded_dict[str(self._module_enum)]['current_scenario'] is not None:

            scenario_found = False
            all_scenarios = ScenariosList()

            for scenario in all_scenarios:
                if scenario.name == loaded_dict[str(self._module_enum)]['current_scenario']:
                    loaded_dict[str(self._module_enum)]['current_scenario'] = scenario
                    scenario_found = True
            if not scenario_found:
                print('WARNING: a scenario setting was applied that referred to a non-existing scenario. It was ignored.')
                loaded_dict[str(self._module_enum)]['current_scenario'] = None
