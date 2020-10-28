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

    @property
    def klass_mp(self):
        from modules.carlainterface.carlainterface_agentclasses.ego_vehicle import EgoVehicle


        return {AgentTypes.EGO_VEHICLE: EgoVehicle
                }[self]

    @property
    def klass_dialog(self):
        from modules.carlainterface.carlainterface_agentclasses.ego_vehicle import EgoVehicleSettingsDialog

        return {AgentTypes.EGO_VEHICLE: EgoVehicleSettingsDialog
                }[self]

    @property
    def shared_variables(self):
        from modules.carlainterface.carlainterface_sharedvalues import EgoVehicleSharedVariables

        return {AgentTypes.EGO_VEHICLE: EgoVehicleSharedVariables
                }[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterface_agentclasses/ui/")

        return {AgentTypes.EGO_VEHICLE: os.path.join(path_to_uis, "ego_vehicle_settings_ui.ui")
                }[self]

    @property
    def hardware_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "carlainterface_agentclasses/ui/")

        return {AgentTypes.EGO_VEHICLE: os.path.join(path_to_uis, "ego_vehicle_tab.ui")
                }[self]

    @property
    def settings(self):
        from modules.carlainterface.carlainterface_settings import EgoVehicleSettings

        return {AgentTypes.EGO_VEHICLE: EgoVehicleSettings
                }[self]

    def __str__(self):
        return {AgentTypes.EGO_VEHICLE: 'Ego Vehicle'
                }[self]
