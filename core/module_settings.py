import inspect
import json
from enum import Enum

from modules.joanmodules import JOANModules


def find_settings_by_identifier(search_dict: dict, identifier: int):
    for key, value in search_dict.items():
        if value.identifier == identifier:
            return key, value
    return None, None


class ModuleSettings:
    def __init__(self, module: JOANModules):
        """
        Initialize
        :param module: module type
        """
        self.module = module

    def save_to_file(self, file_path, keys_to_omit=()):
        """
        Save settings to file
        :param file_path:
        :param keys_to_omit: list with keys / settings to omit in saving to file
        :return:
        """
        dict_to_save = self.as_dict()

        for key in keys_to_omit:
            try:
                del dict_to_save[key]
            except KeyError:
                pass

        with open(file_path, 'w') as settings_file:
            json.dump(dict_to_save, settings_file, sort_keys=True, indent=4)

    def load_from_file(self, file_path):
        """
        Load settings dict from file
        :param file_path:
        """
        with open(file_path, 'r') as settings_file:
            loaded_dict = json.load(settings_file)

        self.load_from_dict(loaded_dict)

    def load_from_dict(self, loaded_dict):
        """
        Set the settings in dict to the settings object
        :param loaded_dict: dictionary with loaded settings (keys, values)
        :return:
        """
        try:
            self._copy_dict_to_class_dict(loaded_dict[str(self.module)], self.__dict__)
        except KeyError:
            warning_message = "WARNING: loading settings for the " + str(self.module) + \
                              " module from a dictionary failed. The loaded dictionary did not contain " + \
                              str(self.module) + " settings." + \
                              (" It did contain settings for: " + ", ".join(loaded_dict.keys()) if loaded_dict.keys() else "")
            print(warning_message)

    def as_dict(self):
        output_dict = {str(self.module): {}}

        # omit attributes of the ABC from the source dict since they are not of interest when displaying the settings as a dict
        source_dict = {key: item for key, item in self.__dict__.items() if
                       key not in ModuleSettings(None).__dict__.keys()}

        self._copy_dict_to_dict(source_dict, output_dict[str(self.module)])
        return output_dict

    def _copy_dict_to_class_dict(self, source, destination):
        """
        method to reconstruct a class dict from a saved dictionary. Recognizes custom class objects and loads their attributes recursively from the sub-dicts
        :param source (dict): saved variables
        :param destination (__dict__): class dict to restore
        :return: None
        """
        keys_to_remove = []
        for key, value in source.items():
            try:
                if isinstance(destination[key], Enum):  # reconstruct the enum from its value
                    destination[key] = value.__class__(value)
                elif hasattr(destination[key], '__dict__') and not inspect.isclass(destination[key]):
                    # recognize child classes and reconstruct their class dicts from the saved dicts
                    self._copy_dict_to_class_dict(value, destination[key].__dict__)
                else:
                    destination[key] = value
            except KeyError:
                print("WARNING: a saved setting called " + key + " was found to restore in " + str(
                    self.module) + " settings, but this setting did not exist. It was created.")
                destination[key] = value

        all_keys = list(destination.keys())
        for key in all_keys:
            if key not in source.keys():
                keys_to_remove.append(key)
                del destination[key]


    @staticmethod
    def _copy_dict_to_dict(source, destination):
        """
        Method to copy a (class) dict to another dictionary. Recognizes all custom classes in the dict and simplifies them to dicts themselves
        :param source (dict): (class) dict
        :param destination (dict): simplified dictionary containing only base type object
        :return: None
        """
        for key, value in source.items():
            if isinstance(value, list):
                destination[key] = ModuleSettings._copy_list_to_list(value)
            elif isinstance(value, dict):
                try:
                    destination[key]  # make sure that the destination dict has an entry at key
                except KeyError:
                    destination[key] = dict()
                ModuleSettings._copy_dict_to_dict(value, destination[key])
            elif isinstance(value, Enum):
                destination[key] = value.value
            elif hasattr(value, '__dict__') and not inspect.isclass(value):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    destination[key] = value.as_dict()
                except AttributeError:
                    destination[key] = dict()
                    ModuleSettings._copy_dict_to_dict(value.__dict__, destination[key])
            else:
                destination[key] = source[key]

    @staticmethod
    def _copy_list_to_list(source):
        """
        Copies a list and simplifies all objects within to base type objects.
        :param source (list): list to copy
        :return: a list containing only base type objects
        """
        output_list = []
        for index, item in enumerate(source):
            if isinstance(item, list):
                output_list.append(ModuleSettings._copy_list_to_list(item))
            elif isinstance(item, Enum):
                print(
                    'WARNING: JOAN settings cannot reconstruct enums embedded in lists from saved files, only the value of the enum will be saved')
                output_list.append(item.value)
            elif hasattr(item, '__dict__') and not inspect.isclass(item):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    output_list.append(item.as_dict())
                except AttributeError:
                    output_list.append(dict())
                    ModuleSettings._copy_dict_to_dict(item.__dict__, output_list[index])
            else:
                output_list.append(item)
        return output_list
