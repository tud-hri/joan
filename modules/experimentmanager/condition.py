import copy

from modules.joanmodules import JOANModules


class Condition:

    def __init__(self, modules_included: list, name):
        self.name = name
        self.diff = {}

        for modules in modules_included:
            self.diff[modules] = {}

    @staticmethod
    def set_from_current_settings(condition_name, parent_experiment, settings_singleton):
        condition = Condition(parent_experiment.modules_included, condition_name)
        for module in parent_experiment.modules_included:
            condition.diff[module] = Condition._get_dict_diff(parent_experiment.base_settings[module],
                                                              copy.deepcopy(settings_singleton.get_settings(module).as_dict())[
                                                                  str(module)], {})

        # return deepcopy of the condition dictionary; else changing a module setting will change the setting across all conditions.
        return condition

    def get_savable_dict(self):
        dict_to_save = {}
        for key, item in self.diff.items():
            dict_to_save[str(key)] = item
        return dict_to_save

    def set_from_loaded_dict(self, loaded_dict):
        for key, item in loaded_dict.items():
            self.diff[JOANModules.from_string_representation(key)] = item

    @staticmethod
    def _get_dict_diff(base_dict, specific_dict, diff_dict):
        """
        Determines the difference between the base dict and a specific dict. If the resulting diff dict is combined with the base dict, the specific dict is
        obtained. This method requires both dicts to have the same set of keys.

        :param base_dict:
        :param specific_dict:
        :return:
        """

        for key in base_dict.keys():
            if key not in specific_dict.keys():
                raise ValueError(
                    'It is not possible to remove_input_device settings that are present in the base of in experiment in a certain condition. '
                    'Conditions can only add or change settings.')

        # TODO: list handling here is pretty inefficient have a look later
        # TODO: if a value is a list (e.g. SW controller), then the complete dict is copied (which is fine, I guess)
        for key, value in base_dict.items():
            if isinstance(value, dict):
                diff_dict[key] = Condition._get_dict_diff(value, specific_dict[key], {})
            elif specific_dict[key] != value:
                diff_dict[key] = specific_dict[key]

        for key in specific_dict.keys():
            if key not in base_dict.keys():
                diff_dict[key] = specific_dict[key]

        return diff_dict
