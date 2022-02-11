import os

from PyQt5 import uic

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from core.statesenum import State
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from modules.carlainterface.scenarios.scenarioslist import ScenariosList
from modules.joanmodules import JOANModules


class CarlaInterfaceDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        """
        :param module_manager: see JOANModules
        :param parent: Needed for Qt windows
        """
        super().__init__(module=JOANModules.CARLA_INTERFACE, module_manager=module_manager, parent=parent)

        # setup dialogs
        self._agent_type_dialog = uic.loadUi(
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         "carlainterface_agentclasses/ui/agent_select_ui.ui"))
        self._agent_type_dialog.btns_agent_type_select.accepted.connect(self._agent_selected)

        # connect buttons
        self.module_widget.btn_add_agent.clicked.connect(self._select_agent_type)
        self._agent_tabs_dict = {}
        self._agent_dialogs_dict = {}

        self._fill_scenarios_combo_box()
        self.module_widget.scenariosComboBox.currentIndexChanged.connect(self.update_scenario)

    def _fill_scenarios_combo_box(self):
        self.module_widget.scenariosComboBox.addItem('', None)
        all_scenarios = ScenariosList()

        for scenario in all_scenarios:
            self.module_widget.scenariosComboBox.addItem(scenario.name, scenario)

    def update_scenario(self):
        selected_scenario = self.module_widget.scenariosComboBox.currentData()
        self.module_manager.module_settings.current_scenario = selected_scenario

    def _handle_state_change(self):
        """"
        This function handles the enabling and disabling of the carla interface change
        """
        super()._handle_state_change()

        is_in_stopped_state = self.module_manager.state_machine.current_state == State.STOPPED

        self.module_widget.groupbox_agents.setEnabled(is_in_stopped_state)
        self.module_widget.btn_add_agent.setEnabled(is_in_stopped_state)
        self.module_widget.scenariosComboBox.setEnabled(is_in_stopped_state)

    def _select_agent_type(self):
        self._agent_type_dialog.combo_agent_type.clear()
        for agents in AgentTypes:
            self._agent_type_dialog.combo_agent_type.addItem(agents.__str__(), userData=agents)
        self._agent_type_dialog.show()

    def _agent_selected(self):
        selected_agent = self._agent_type_dialog.combo_agent_type.itemData(
            self._agent_type_dialog.combo_agent_type.currentIndex())
        # module_manager manages adding a new hardware agent
        self.module_manager.add_agent(selected_agent, from_button=True)

    def update_dialog(self):
        difference_dict = {k: self._agent_tabs_dict[k] for k in
                           set(self._agent_tabs_dict) - set(self.module_manager.module_settings.agents)}
        for key in difference_dict:
            self.remove_agent(key)
        for agent_settings in self.module_manager.module_settings.agents:
            if self.module_manager.module_settings.agents[agent_settings].identifier not in self._agent_tabs_dict:
                self.add_agent(self.module_manager.module_settings.agents[agent_settings], False)
            self._agent_dialogs_dict[
                self.module_manager.module_settings.agents[agent_settings].identifier].display_values(
                self.module_manager.module_settings.agents[agent_settings])

        selected_scenario = self.module_manager.module_settings.current_scenario
        if selected_scenario:
            self.module_widget.scenariosComboBox.setCurrentText(selected_scenario.name)

    def add_agent(self, settings, from_button):
        """
        :param setting: contains all settings
        :param from_button: boolean to prevent showing more than one window
        """
        agent_type = AgentTypes(settings.agent_type)

        # Adding tab
        agent_tab = uic.loadUi(agent_type.agent_tab_ui_file)
        agent_tab.group_agent.setTitle(settings.identifier)

        # Adding dialog
        agent_dialog = agent_type.settings_dialog(settings=settings, module_manager=self.module_manager, parent=self)

        # Connecting buttons
        agent_tab.btn_settings.clicked.connect(lambda: agent_dialog.show())
        agent_tab.btn_remove_agent.clicked.connect(lambda: self.module_manager.remove_agent(settings.identifier))

        # add to module_dialog widget
        self._agent_tabs_dict[settings.identifier] = agent_tab
        self._agent_dialogs_dict[settings.identifier] = agent_dialog
        self.module_widget.agent_list_layout.addWidget(agent_tab)

        if from_button:
            agent_dialog.show()

    def remove_agent(self, identifier):
        # remove agent tab
        self._agent_tabs_dict[identifier].setParent(None)
        del self._agent_dialogs_dict[identifier]
        del self._agent_tabs_dict[identifier]
