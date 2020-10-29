import enum

from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules
from modules.carlainterface.carlainterface_agenttypes import AgentTypes

class CarlaInterfaceSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.CARLA_INTERFACE)
        self.temp = 0
        self.ego_vehicles = {}

    def remove_agent(self, setting):
        if isinstance(setting, EgoVehicleSettings):
            self.ego_vehicles.pop(setting.identifier)

class EgoVehicleSettings:
    """
    Class containing the default settings for an egovehicle
    """

    def __init__(self, agent_type: AgentTypes = AgentTypes.EGO_VEHICLE, identifier = 0):
        """
        Initializes the class with default variables
        """
        self.selected_input = 'None'
        self.selected_controller = 'None'
        self.selected_spawnpoint = 'None'
        self.selected_car = 'hapticslab.audi'
        self.velocity = 80
        self.set_velocity = False
        self.name = ''
        self.identifier = identifier

        self.input_type = agent_type

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)