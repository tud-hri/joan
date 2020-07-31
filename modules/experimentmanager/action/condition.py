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
            condition.diff[module] = Condition._get_dict_diff(parent_experiment.base_settings[module].as_dict()[str(module)], settings_singleton.get_settings(module).as_dict()[str(module)], {})

        return condition

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
                raise ValueError('It is not possible to remove settings that are present in the base of in experiment in a certain condition. '
                                 'Conditions can only add or change settings.')

        # todo: list handling here is pretty inefficient have a look later
        for key, value in base_dict.items():
            if type(value) is dict:
                return Condition._get_dict_diff(value, specific_dict[key], diff_dict)
            if specific_dict[key] != value:
                diff_dict[key] = specific_dict[key]

        for key in specific_dict.keys():
            if key not in base_dict.keys():
                diff_dict[key] = specific_dict[key]

        return diff_dict
