from .scenario import Scenario
from modules.scenarios.action.scenariosaction import ScenariosAction
from modules.joanmodules import JOANModules


class ExamplePrintScenario(Scenario):
    def __init__(self):
        super().__init__()

        self.keyboard_message_send = False

    def do_function(self, scenarios_action: ScenariosAction):
        if not self.keyboard_message_send:
            for hardware_name in scenarios_action.read_news(JOANModules.HARDWARE_MANAGER).keys():
                if 'Keyboard' in hardware_name:
                    print('A keyboard is active')
                    self.keyboard_message_send = True


    @property
    def name(self):
        return 'Print scenario'
