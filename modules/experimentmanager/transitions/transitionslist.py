import glob
import importlib
import os


class TransitionsList(list):
    """
    a list object that is automatically filled with all available transitions in the transitions folder. This list makes your custom transition available in
    JOAN automatically if you've added it to the transitions folder.
    """

    def __init__(self):
        super().__init__()

        python_modules_in_transitions = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))

        for path_to_module in python_modules_in_transitions:
            module_name = path_to_module.split(os.sep)[-1].replace('.py', '')

            if module_name not in ['__init__', 'transition', 'transitionslist']:

                imported_module = importlib.import_module('.' + module_name, __package__)

                for imported_class_name in dir(imported_module):
                    if imported_class_name != 'Transition' and imported_class_name[0] != '_':
                        transition_object = getattr(imported_module, imported_class_name)()
                        self.append(transition_object)
