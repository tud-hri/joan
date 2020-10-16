import enum
import os

from .carlainterfacesettings import TrafficVehicleSettings, EgoVehicleSettings

class AgentTypes(enum.Enum):
    """
    Enum to represent all available steering wheel controllers.
    """
    EGOVEHICLE = 0
    TRAFFICVEHICLE = 1

    @property
    def klass(self):
        from .agents.egovehicle import EgoVehicle
        from .agents.trafficvehicle import TrafficVehicle

        return {AgentTypes.EGOVEHICLE: EgoVehicle,
                AgentTypes.TRAFFICVEHICLE: TrafficVehicle}[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "agents/ui/")
        return {AgentTypes.EGOVEHICLE: os.path.join(path_to_uis, "ego_vehicle_settings_ui.uis"),
                AgentTypes.TRAFFICVEHICLE: os.path.join(path_to_uis, "traffic_vehicle_settings_ui.uis")}[self]

    @property
    def agent_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dialog/ui/")
        return {AgentTypes.EGOVEHICLE: os.path.join(path_to_uis, "ego_vehicle_tab.uis"),
                AgentTypes.TRAFFICVEHICLE: os.path.join(path_to_uis, "traffic_vehicle_tab.uis")}[self]

    @property
    def settings(self):
        return {AgentTypes.EGOVEHICLE: EgoVehicleSettings(),
                AgentTypes.TRAFFICVEHICLE: TrafficVehicleSettings()}[self]

    def __str__(self):
        return {AgentTypes.EGOVEHICLE: 'EgoVehicle',
                AgentTypes.TRAFFICVEHICLE: 'TrafficVehicle'}[self]
