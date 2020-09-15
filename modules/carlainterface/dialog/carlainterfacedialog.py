import os

from PyQt5 import uic

from modules.joanmodules import JOANModules
from core.joanmoduleaction import JoanModuleAction
from core.joanmoduledialog import JoanModuleDialog
from core.statesenum import State
from modules.carlainterface.action.agenttypes import AgentTypes

class CarlaInterfaceDialog(JoanModuleDialog):
    """
    This class is the actual dialog you see when you open up the module. Mostly this class serves as a
    connection between the user and the 'brains', which is the action module.
    """

    def __init__(self, module_action: JoanModuleAction, parent=None):
        """
        Initializes the class
        :param module_action:
        :param parent:
        """
        super().__init__(module=JOANModules.CARLA_INTERFACE, module_action=module_action, parent=parent)

        # initialize variables
        self.connected_carla = False
        self.old_nr_cars = 0
        self.i = 1

        self.module_widget.btn_spawn_all.clicked.connect(self.module_action.spawn_all)
        self.module_widget.btn_destroy_all.clicked.connect(self.module_action.destroy_all)
        self.module_widget.btn_remove_all.clicked.connect(self.module_action.remove_all)

        self.module_widget.btnDisconnect.clicked.connect(self.module_action.disconnect_carla)
        self.module_widget.groupVehicles.setEnabled(False)
        self.module_widget.btn_add_agent.setEnabled(False)
        self.module_widget.btnDisconnect.setEnabled(False)
        self.module_widget.btn_spawn_all.setEnabled(False)
        self.module_widget.btn_destroy_all.setEnabled(False)
        self.module_widget.btn_remove_all.setEnabled(False)

        # setup dialogs
        self._agent_type_dialog = uic.loadUi(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/agent_select_ui.ui"))
        self._agent_type_dialog.btns_agent_type_select.accepted.connect(self.add_selected_agent)

        # connect buttons
        self.module_widget.btn_add_agent.clicked.connect(self._agent_selection)


    def handle_state_change(self):
        """"
        This function handles the enabling and disabling of the carla interface change
        """
        super().handle_state_change()

        self.connected_carla = self.module_action.check_connection()
        # link the spawning of vehicles to connected state
        # make sure you can only disconnect in the ready state
        if self.module_action.state_machine.current_state == State.READY:
            self.load_settings.setEnabled(self.connected_carla)
            self.module_widget.btnDisconnect.setEnabled(True)
            self.module_widget.groupVehicles.setEnabled(self.connected_carla)
            self.module_widget.btn_add_agent.setEnabled(self.connected_carla)
            self.module_widget.btn_spawn_all.setEnabled(self.connected_carla)
            self.module_widget.btn_destroy_all.setEnabled(self.connected_carla)
            self.module_widget.btn_remove_all.setEnabled(self.connected_carla)
        elif self.module_action.state_machine.current_state == State.RUNNING:
            self.load_settings.setEnabled(False)
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.btn_add_agent.setEnabled(False)
            self.module_widget.btn_spawn_all.setEnabled(False)
            self.module_widget.btn_destroy_all.setEnabled(False)
            self.module_widget.btn_remove_all.setEnabled(False)
        elif self.module_action.state_machine.current_state == State.ERROR:
            self.load_settings.setEnabled(False)
            self.module_widget.btnDisconnect.setEnabled(False)
            self.module_widget.btn_add_agent.setEnabled(False)
            self.module_widget.btn_spawn_all.setEnabled(False)
            self.module_widget.btn_destroy_all.setEnabled(False)
            self.module_widget.btn_remove_all.setEnabled(False)
        else:
            self.load_settings.setEnabled(False)
            self.module_widget.btnDisconnect.setEnabled(False)
            # self.module_widget.groupVehicles.setEnabled(False)
            self.module_widget.btn_add_agent.setEnabled(False)
            self.module_widget.btn_spawn_all.setEnabled(False)
            self.module_widget.btn_destroy_all.setEnabled(False)
            self.module_widget.btn_remove_all.setEnabled(False)

    def _agent_selection(self):
        self._agent_type_dialog.combo_agent_type.clear()
        for agents in AgentTypes:
            self._agent_type_dialog.combo_agent_type.addItem(agents.__str__(),
                                                                             userData=agents)
        self._agent_type_dialog.show()

    def add_selected_agent(self):
        chosen_agent = self._agent_type_dialog.combo_agent_type.itemData(
            self._agent_type_dialog.combo_agent_type.currentIndex())
        self.module_action.add_agent(chosen_agent)

    def disconnect_carla(self, connected):
        """
        This function disconnects from carla, when it does it will also automatically destroy any cars that were spawned
        in the simulation.
        """
        self.connected_carla = connected
        self.module_widget.groupVehicles.setEnabled(self.connected_carla)
        self.module_widget.btn_add_agent.setEnabled(self.connected_carla)
        self.module_widget.btnDisconnect.setEnabled(self.connected_carla)

