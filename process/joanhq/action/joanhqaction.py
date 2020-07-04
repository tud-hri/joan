"""Action class for JOAN menu"""
import os
from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process import News
from process import Settings


class JoanHQAction(QtCore.QObject):
    """Action class for JoanHQ"""

    def __init__(self):
        super(QtCore.QObject, self).__init__()

        self.window = None

        # settings
        self.singleton_settings = Settings()

        # path to modules directory
        self.path_modules = os.path.normpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "modules"))

        # dictionary to keep track of the instantiated modules
        self._instantiated_modules = {}

    def initialize_all(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.initialize()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.initialize()

    def start_all(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.start()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.start()

    def stop_all(self):
        """Stop all modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.stop()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.stop()

    def add_module(self, module: JOANModules, name='', parent=None, millis=100):
        """Add module, instantiated module, find unique name"""

        if not parent:
            parent = self.window

        module_action = module.action(millis=millis)
        module_dialog = module.dialog(module_action, parent=parent)

        self.window.add_module(module_dialog, module)

        # add instantiated module to dictionary
        self._instantiated_modules[module] = module_action

        return module_dialog, module_action

    def remove_module(self, module: JOANModules):
        """ Remove module by name"""

        del self._instantiated_modules[module]

    def emergency(self):
        """Emergency button processing"""
        self.stop_all()

    def quit(self):
        self.stop_all()

    @property
    def instantiated_modules(self):
        """getter for self._instantiated_modules, only allow get, not set"""
        return self._instantiated_modules
