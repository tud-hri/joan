from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
import os
from PyQt5 import uic
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from core.statesenum import State

class CarlaInterfaceDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.CARLA_INTERFACE, module_manager=module_manager, parent=parent)
        """
        Initializes the class
        :param module_manager:
        :param parent:
        """
        # initialize variables
        self.connected_carla = False
        self.old_nr_cars = 0
        self.i = 1
        self._agent_tabs_dict = {}

        # setup dialogs
        self._agent_type_dialog = uic.loadUi(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterface_agentclasses/ui/agent_select_ui.ui"))
        self._agent_type_dialog.btns_agent_type_select.accepted.connect(self.add_selected_agent)

        # connect buttons
        # TODO have to add the connect and disconnect button of main to the connect function
        self._module_widget.btn_add_agent.clicked.connect(self._agent_selection)

    def _handle_state_change(self):
        """"
        This function handles the enabling and disabling of the carla interface change
        """
        super()._handle_state_change()
        if self.module_manager.state_machine.current_state == State.STOPPED:
            self._module_widget.groupbox_agents.setEnabled(True)
        else:
            self._module_widget.groupbox_agents.setEnabled(False)

    def _agent_selection(self):
        self._agent_type_dialog.combo_agent_type.clear()
        for agents in AgentTypes:
            self._agent_type_dialog.combo_agent_type.addItem(agents.__str__(),
                                                             userData=agents)
        self._agent_type_dialog.show()

    def add_selected_agent(self):
        chosen_agent = self._agent_type_dialog.combo_agent_type.itemData(
            self._agent_type_dialog.combo_agent_type.currentIndex())
        agent_name = self.module_manager._add_agent(chosen_agent)

        # Adding tab
        self._agent_tabs_dict[agent_name] = uic.loadUi(chosen_agent.hardware_tab_ui_file)
        self._agent_tabs_dict[agent_name].group_agent.setTitle(agent_name)
        self._module_widget.agent_list_layout.addWidget(self._agent_tabs_dict[agent_name])

        # Connecting buttons
        self._agent_tabs_dict[agent_name].btn_settings.clicked.connect(
            lambda: self.module_manager._open_settings_dialog(agent_name))
        self._agent_tabs_dict[agent_name].btn_remove_agent.clicked.connect(lambda: self._remove_agent(agent_name))
        # self.module_manager._open_settings_dialog(agent_name)

    def _remove_agent(self, agent_name):
        # Remove dialog
        self._agent_tabs_dict[agent_name].setParent(None)
        del self._agent_tabs_dict[agent_name]

        # We remove the settings dialog and settings object in the module_manager class
        self.module_manager._remove_agent(agent_name)
