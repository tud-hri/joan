import enum

from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class CarlaInterfaceSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.CARLA_INTERFACE)
        self.temp = 0


class EgoVehicleSettings:
    """
    Class containing the default settings for an egovehicle
    """

    def __init__(self):
        """
        Initializes the class with default variables
        """
        self.selected_input = 'None'
        self.selected_controller = 'None'
        self.selected_spawnpoint = 0
        self.selected_car = 'hapticslab.audi'
        self.velocity = 80
        self.set_velocity = False
        self.name = ''

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)