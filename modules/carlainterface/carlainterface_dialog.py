from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
import os
from PyQt5 import uic
from modules.carlainterface.carlainterface_agenttypes import AgentTypes

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
        # self._module_widget.btn_spawn_all.clicked.connect(self.module_manager.spawn_all)
        # self._module_widget.btn_destroy_all.clicked.connect(self.module_manager.destroy_all)
        # self._module_widget.btn_remove_all.clicked.connect(self.module_manager.remove_all)
        #
        # self._module_widget.btn_disconnect.clicked.connect(self.module_manager.disconnect_carla)
        # self._module_widget.btn_connect.clicked.connect(self.module_manager.connect_carla)
        # self._module_widget.groupVehicles.setEnabled(False)
        # self._module_widget.btn_add_agent.setEnabled(False)
        # self._module_widget.btn_disconnect.setEnabled(False)
        # self._module_widget.btn_spawn_all.setEnabled(False)
        # self._module_widget.btn_destroy_all.setEnabled(False)
        # self._module_widget.btn_remove_all.setEnabled(False)

        # setup dialogs
        self._agent_type_dialog = uic.loadUi(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterface_agentclasses/ui/agent_select_ui.ui"))
        self._agent_type_dialog.btns_agent_type_select.accepted.connect(self.add_selected_agent)

        # connect buttons
        self._module_widget.btn_add_agent.clicked.connect(self._agent_selection)

    def handle_state_change(self):
        """"
        This function handles the enabling and disabling of the carla interface change
        """
        super().handle_state_change()

        self.connected_carla = self.module_manager.check_connection()
        # make sure you can only disconnect in the ready state
        if self.module_manager.state_machine.current_state == State.READY:
            self.load_settings.setEnabled(self.connected_carla)
            self._module_widget.groupVehicles.setEnabled(self.connected_carla)
            self._module_widget.btn_add_agent.setEnabled(self.connected_carla)
            self._module_widget.btn_spawn_all.setEnabled(self.connected_carla)
            self._module_widget.btn_destroy_all.setEnabled(self.connected_carla)
            self._module_widget.btn_remove_all.setEnabled(self.connected_carla)
        elif self.module_manager.state_machine.current_state == State.RUNNING:
            self.load_settings.setEnabled(False)
            self._module_widget.btn_add_agent.setEnabled(False)
            self._module_widget.btn_spawn_all.setEnabled(False)
            self._module_widget.btn_destroy_all.setEnabled(False)
            self._module_widget.btn_remove_all.setEnabled(False)
        elif self.module_manager.state_machine.current_state == State.ERROR:
            self.load_settings.setEnabled(False)
            self._module_widget.btn_add_agent.setEnabled(False)
            self._module_widget.btn_spawn_all.setEnabled(False)
            self._module_widget.btn_destroy_all.setEnabled(False)
            self._module_widget.btn_remove_all.setEnabled(False)
        else:
            self.load_settings.setEnabled(False)
            # self._module_widget.groupVehicles.setEnabled(False)
            self._module_widget.btn_add_agent.setEnabled(False)
            self._module_widget.btn_spawn_all.setEnabled(False)
            self._module_widget.btn_destroy_all.setEnabled(False)
            self._module_widget.btn_remove_all.setEnabled(False)

    def _agent_selection(self):
        self._agent_type_dialog.combo_agent_type.clear()
        for agents in AgentTypes:
            self._agent_type_dialog.combo_agent_type.addItem(agents.__str__(),
                                                             userData=agents)
        self._agent_type_dialog.show()

    def add_selected_agent(self):
        chosen_agent = self._agent_type_dialog.combo_agent_type.itemData(
            self._agent_type_dialog.combo_agent_type.currentIndex())
        self.module_manager.add_agent(chosen_agent)

    def disconnect_carla(self, connected):
        """
        This function disconnects from carla, when it does it will also automatically destroy any cars that were spawned
        in the simulation.
        """
        self.connected_carla = connected
        self._module_widget.groupVehicles.setEnabled(self.connected_carla)
        self._module_widget.btn_add_agent.setEnabled(self.connected_carla)
        self._module_widget.btn_disconnect.setEnabled(self.connected_carla)