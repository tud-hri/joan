import copy
import json

from process import Settings
from modules.joanmodules import JOANModules
from .condition import Condition


class Experiment:
    def __init__(self, modules_included: list):
        self.modules_included = modules_included
        self.base_settings = {}

        self.all_conditions = []
        self.active_condition_sequence = []

    def set_from_current_settings(self, settings_singleton: Settings):
        if self.all_conditions:
            raise RuntimeError("The base settings of an experiment can only be modified when no conditions exist.")

        for module in self.modules_included:
            self.base_settings[module] = copy.deepcopy(settings_singleton.get_settings(module).as_dict())

    def save_to_file(self, file_path):
        dict_to_save = {'modules_included': [str(module) for module in self.modules_included],
                        'base_settings': {},
                        'conditions': {},
                        'active_condition_sequence': [condition.name for condition in self.active_condition_sequence], }

        for module in self.modules_included:
            dict_to_save['base_settings'].update(self.base_settings[module])

        for condition in self.all_conditions:
            dict_to_save['conditions'][condition.name] = condition.get_savable_dict()

        with open(file_path, 'w') as settings_file:
            json.dump(dict_to_save, settings_file, indent=4)

    @staticmethod
    def load_from_file(file_path):

        with open(file_path, 'r') as settings_file:
            loaded_dict = json.load(settings_file)

        modules_included = [JOANModules.from_string_representation(string) for string in loaded_dict['modules_included']]
        new_experiment = Experiment(modules_included)

        for module in modules_included:
            new_experiment.base_settings[module] = loaded_dict['base_settings'][str(module)]

        # TODO all_conditions and active_conditions does not seem to work
        for condition_name, diff_dict in loaded_dict['conditions'].items():
            new_condition = Condition(modules_included, condition_name)
            new_condition.set_from_loaded_dict(diff_dict)
            new_experiment.all_conditions.append(new_condition)

        for condition_name in loaded_dict['active_condition_sequence']:
            condition_found = False
            for condition in new_experiment.all_conditions:
                if condition_name == condition.name:
                    new_experiment.active_condition_sequence.append(condition)
                    condition_found = True
            if not condition_found:
                print('WARNING: a condition named: "' + condition_name + '" was used in the loaded experiment. But this condition does not exist in the '
                                                                         'experiment. It was ignored. ')

        return new_experiment
