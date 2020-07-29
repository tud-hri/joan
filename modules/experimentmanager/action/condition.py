class Condition:

    def __init__(self, modules_included: list):
        self.diff = {}

        for modules in modules_included:
            self.diff[modules] = {}

    def set_from_current_settings(self, parent_experiment, settings_singleton):
        for module in parent_experiment.modules_included:
            self.diff[module] = self._get_dict_diff(parent_experiment.base_settings[module], settings_singleton.get_settings(module).as_dict())

    @staticmethod
    def _get_dict_diff(base_dict, specific_dict):
        """
        Determines the difference between the base dict and a specific dict. If the resulting diff dict is combined with the base dict, the specific dict is
        obtained. This method requires both dicts to have the same set of keys.

        :param base_dict:
        :param specific_dict:
        :return:
        """
        if base_dict.keys() - specific_dict.keys():
            raise RuntimeError("The current settings have different settings than the base settings of this experiment. Make sure both the base settings and "
                               "the condition settings are generated in the same version of joan.")

        diff_dict = {}

        for key, value in base_dict:
            if specific_dict[key] != value:
                diff_dict[key] = specific_dict[key]
