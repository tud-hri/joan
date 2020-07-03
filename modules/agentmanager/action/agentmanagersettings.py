import inspect

from PyQt5 import QtGui
from enum import Enum

from process.joanmodulesettings import JoanModuleSettings
from modules.joanmodules import JOANModules


class AgentManagerSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        super().__init__(module_enum)

        self.ego_vehicles = []
        self.traffic_vehicles = []


    def set_from_loaded_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        try:
            module_settings_to_load = loaded_dict[str(self._module_enum)]
        except KeyError:
            warning_message = "WARNING: loading settings for the " + str(self._module_enum) + \
                              " module from a dictionary failed. The loaded dictionary did not contain " + str(self._module_enum) + " settings." + \
                              (" It did contain settings for: " + ", ".join(loaded_dict.keys()) if loaded_dict.keys() else "")
            print(warning_message)
            return

        self.ego_vehicles = []
        for egovehicle_settings_dict in module_settings_to_load['key_boards']:
            egovehicle_settings = EgoVehicleSettings()
            egovehicle_settings.set_from_loaded_dict(egovehicle_settings_dict)
            self.ego_vehicles.append(egovehicle_settings)

        self.traffic_vehicles = []
        for trafficvehicle_settings_dict in module_settings_to_load['joy_sticks']:
            trafficvehicle_settings = TrafficVehicleSettings()
            trafficvehicle_settings.set_from_loaded_dict(trafficvehicle_settings_dict)
            self.traffic_vehicles.append(trafficvehicle_settings)


    @staticmethod
    def _copy_dict(source, destination):
        for key, value in source.items():
            if isinstance(value, list):
                destination[key] = AgentManagerSettings._copy_list(value)
            elif isinstance(value, dict):
                try:
                    destination[key]  # make sure that the destination dict has an entry at key
                except KeyError:
                    destination[key] = dict()
                AgentManagerSettings._copy_dict(value, destination[key])
            elif hasattr(value, '__dict__') and not isinstance(value, Enum) and not inspect.isclass(value):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    destination[key] = value.as_dict()
                except NotImplementedError:
                    destination[key] = dict()
                    AgentManagerSettings._copy_dict(value.__dict__, destination[key])
            else:
                destination[key] = source[key]

    @staticmethod
    def _copy_list(source):
        output_list = []
        for index, item in enumerate(source):
            if isinstance(item, list):
                output_list.append(AgentManagerSettings._copy_list(item))
            elif hasattr(item, '__dict__') and not isinstance(item, Enum) and not inspect.isclass(item):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    output_list.append(item.as_dict())
                except NotImplementedError:
                    output_list.append(dict())
                    AgentManagerSettings._copy_dict(item.__dict__, output_list[index])
            else:
                output_list.append(item)
        return output_list

class EgoVehicleSettings():
    def __init__(self):
        self.spawn_point_nr = 0

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

class TrafficVehicleSettings():
    def __init__(self):
        self.spawn_point_nr = 0

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)