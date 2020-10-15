import glob
import importlib
import os


class ScenariosList(list):

    def __init__(self):
        super().__init__()

        python_modules_in_scenarios = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))

        for path_to_module in python_modules_in_scenarios:
            module_name = path_to_module.split(os.sep)[-1].replace('.py', '')

            if module_name not in ['__init__', 'scenario', 'scenarioslist']:

                imported_module = importlib.import_module('.' + module_name, __package__)

                for imported_class_name, item in imported_module.__dict__.items():
                    if isinstance(item, type) and item.__module__ == __package__ + '.' + module_name:
                        scenario_object = getattr(imported_module, imported_class_name)()
                        self.append(scenario_object)
