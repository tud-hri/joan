import inspect
from enum import Enum

from modules.joanmodules import JOANModules
from core.modulesettings import ModuleSettings


class CarlaInterfaceSettings(ModuleSettings):
    """
    Class containing the different settings for multiple agents, inherits from ModuleSettings
    """

    def __init__(self, module_enum: JOANModules):
        super().__init__(module_enum)

        self.ego_vehicles = []
        self.traffic_vehicles = []

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        try:
            self.before_load_settings.emit()
            module_settings_to_load = loaded_dict[str(self._module_enum)]
        except KeyError:
            warning_message = "WARNING: loading settings for the " + str(self._module_enum) + \
                              " module from a dictionary failed. The loaded dictionary did not contain " + str(
                self._module_enum) + " settings." + \
                              (" It did contain settings for: " + ", ".join(
                                  loaded_dict.keys()) if loaded_dict.keys() else "")
            print(warning_message)
            return

        # remove old existing settings
        while self.ego_vehicles:
            vehicle = self.ego_vehicles.pop()
            del vehicle

        while self.traffic_vehicles:
            vehicle = self.traffic_vehicles.pop()
            del vehicle

        for egovehicle_settings_dict in module_settings_to_load['ego_vehicles']:
            egovehicle_settings = EgoVehicleSettings()
            egovehicle_settings.set_from_loaded_dict(egovehicle_settings_dict)
            self.ego_vehicles.append(egovehicle_settings)

        for trafficvehicle_settings_dict in module_settings_to_load['traffic_vehicles']:
            trafficvehicle_settings = TrafficVehicleSettings()
            trafficvehicle_settings.set_from_loaded_dict(trafficvehicle_settings_dict)
            self.traffic_vehicles.append(trafficvehicle_settings)

        self.load_settings_done.emit()

    @staticmethod
    def _copy_dict(source, destination):
        for key, value in source.items():
            if isinstance(value, list):
                destination[key] = CarlaInterfaceSettings._copy_list(value)
            elif isinstance(value, dict):
                try:
                    destination[key]  # make sure that the destination dict has an entry at key
                except KeyError:
                    destination[key] = dict()
                CarlaInterfaceSettings._copy_dict(value, destination[key])
            elif hasattr(value, '__dict__') and not isinstance(value, Enum) and not inspect.isclass(value):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    destination[key] = value.as_dict()
                except NotImplementedError:
                    destination[key] = dict()
                    CarlaInterfaceSettings._copy_dict(value.__dict__, destination[key])
            else:
                destination[key] = source[key]

    @staticmethod
    def _copy_list(source):
        output_list = []
        for index, item in enumerate(source):
            if isinstance(item, list):
                output_list.append(CarlaInterfaceSettings._copy_list(item))
            elif hasattr(item, '__dict__') and not isinstance(item, Enum) and not inspect.isclass(item):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    output_list.append(item.as_dict())
                except NotImplementedError:
                    output_list.append(dict())
                    CarlaInterfaceSettings._copy_dict(item.__dict__, output_list[index])
            else:
                output_list.append(item)
        return output_list

    def remove_agent(self, setting):
        if isinstance(setting, EgoVehicleSettings):
            self.ego_vehicles.remove(setting)

        if isinstance(setting, TrafficVehicleSettings):
            self.traffic_vehicles.remove(setting)



class EgoVehicleSettings():
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


class TrafficVehicleSettings():
    """
    Class containing the default settings for a traffic vehicle.
    """

    def __init__(self):
        """
        initializes the class with default variables
        """
        self.velocity = 50
        self.trajectory_name = 'TestTrajectory2.csv'
        self.selected_spawnpoint = 0
        self.selected_car = 'hapticslab.audi'
        self.t_lookahead = 0.6
        self.w_lat = 1
        self.w_heading = 2
        self.k_p = 6
        self.k_d = 2.5
        self.set_velocity_with_pd = False
        self.name = ''

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
