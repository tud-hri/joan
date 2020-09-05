from PyQt5 import QtWidgets

from core.statesenum import State
from core.joanmoduledialog import JoanModuleDialog
from modules.joanmodules import JOANModules
from modules.scenarios.scenarios.scenarioslist import ScenariosList


class ScenariosDialog(JoanModuleDialog):
    def __init__(self, module_action, parent=None):
        super().__init__(JOANModules.SCENARIOS, module_action, parent=parent)

        self.module_widget.scenariosComboBox.currentIndexChanged.connect(self.update_scenario)

        self._fill_scenarios_combo_box()
        self.module_action.state_machine.add_state_change_listener(self._state_changed)

    def _fill_scenarios_combo_box(self):
        self.module_widget.scenariosComboBox.addItem('', None)
        all_scenarios = ScenariosList()

        for scenario in all_scenarios:
            self.module_widget.scenariosComboBox.addItem(scenario.name, scenario)

    def update_scenario(self):
        selected_scenario = self.module_widget.scenariosComboBox.currentData()
        self.module_action.settings.current_scenario = selected_scenario

    def _state_changed(self):
        new_state = self.module_action.state_machine.current_state
        self.module_widget.scenariosComboBox.setEnabled(new_state is State.IDLE or new_state is State.READY)
