import copy

from process import Settings


class Experiment:
    def __init__(self, modules_included: list):
        self.modules_included = modules_included
        self.base_settings = {}
        # TODO: this (base settings) is currently a dict with settings object. Maybe it's more convenient to make this a complete nested dict representation

        self.all_conditions = []
        self.active_condition_sequence = []

    def set_from_current_settings(self, settings_singleton: Settings):
        if self.all_conditions:
            raise RuntimeError("The base settings of an experiment can only be modified when no conditions exist.")

        for module in self.modules_included:
            self.base_settings[module] = copy.deepcopy(settings_singleton.get_settings(module))

    def save_to_file(self, file_path):
        pass  # TODO: implement this

    @staticmethod
    def load_from_file(file_path):
        pass  # TODO: implement this
