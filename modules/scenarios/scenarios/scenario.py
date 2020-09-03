import abc
from modules.scenarios.action.scenariosaction import ScenariosAction


class Scenario:
    @abc.abstractmethod
    def do_function(self, scenarios_action: ScenariosAction):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass
