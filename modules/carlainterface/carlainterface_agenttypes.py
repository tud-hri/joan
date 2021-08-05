import enum
import os


class AgentTypes(enum.Enum):
    """
    Enumeration class for all the different hardware types available. Contains:
    klass_mp: the class that runs in a seperate multiprocess which loops
    klass_dialog: the settings dialog of the input type
    shared_variables: the variables that need to be shared from the hardwareinpute type with the manager
    settings_ui_file: ui file of the settings dialog
    hardware_tab_uifile: ui file of the widget added in the module dialog
    settings: specific settings of the hardware input type
    __str__: the string represntation of the hardware input type

    """

    EGO_VEHICLE = 0
    NPC_VEHICLE = 1

    @property
    def process(self):
        from modules.carlainterface.carlainterface_agentclasses.ego_vehicle import EgoVehicleProcess
        from modules.carlainterface.carlainterface_agentclasses.npc_vehicle import NPCVehicleProcess

        return {AgentTypes.EGO_VEHICLE: EgoVehicleProcess,
                AgentTypes.NPC_VEHICLE: NPCVehicleProcess
                }[self]

    @property
    def settings_dialog(self):
        from modules.carlainterface.carlainterface_agentclasses.ego_vehicle import EgoVehicleSettingsDialog
        from modules.carlainterface.carlainterface_agentclasses.npc_vehicle import NPCVehicleSettingsDialog

        return {AgentTypes.EGO_VEHICLE: EgoVehicleSettingsDialog,
                AgentTypes.NPC_VEHICLE: NPCVehicleSettingsDialog
                }[self]

    @property
    def shared_variables(self):
        from modules.carlainterface.carlainterface_sharedvariables import VehicleSharedVariables

        return VehicleSharedVariables

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterface_agentclasses/ui/")

        return {AgentTypes.EGO_VEHICLE: os.path.join(path_to_uis, "ego_vehicle_settings_ui.ui"),
                AgentTypes.NPC_VEHICLE: os.path.join(path_to_uis, "npc_vehicle_settings_ui.ui")
                }[self]

    @property
    def agent_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterface_agentclasses/ui/")

        return os.path.join(path_to_uis, "agent_tab.ui")

    @property
    def settings(self):
        from modules.carlainterface.carlainterface_agentclasses.ego_vehicle import EgoVehicleSettings
        from modules.carlainterface.carlainterface_agentclasses.npc_vehicle import NPCVehicleSettings

        return {AgentTypes.EGO_VEHICLE: EgoVehicleSettings,
                AgentTypes.NPC_VEHICLE: NPCVehicleSettings
                }[self]

    def __str__(self):
        return {AgentTypes.EGO_VEHICLE: 'Ego Vehicle',
                AgentTypes.NPC_VEHICLE: 'NPC Vehicle'
                }[self]
