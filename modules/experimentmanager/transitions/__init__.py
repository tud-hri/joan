import glob
import importlib
import os

python_modules = glob.glob(os.path.join(os.path.dirname(__file__), '*.py'))
imported_class_name, module_name, module = ('', '', '')
for module in python_modules:
    module_name = module.split('\\')[-1].replace('.py', '')
    if module.split('\\')[-1] not in ['__init__.py', 'transition.py']:
        imported_module = importlib.import_module('.' + module_name, __package__)

        for imported_class_name in dir(imported_module):
            if imported_class_name != 'Transition' and imported_class_name[0] != '_':
                locals()[imported_class_name] = getattr(imported_module, imported_class_name)
        del locals()[module_name], imported_module

del glob, os, importlib, imported_class_name, module_name, module, python_modules
