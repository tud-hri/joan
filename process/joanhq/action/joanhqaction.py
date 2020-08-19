"""Action class for JOAN menu"""
import os
from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process import News
from process import Settings


class JoanHQAction(QtCore.QObject):
    """
    Action class for JoanHQ
    """

    def __init__(self):
        """
        Initialize
        """
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
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            try:
                module.action.initialize()
            except AttributeError:  # module has new style TODO: remove_input_device statement above when moving to new style
                module.initialize()

    def start_all(self):
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            try:
                module.action.start()
            except AttributeError:  # module has new style TODO: remove_input_device statement above when moving to new style
                module.start()

    def stop_all(self):
        """
        Stop all modules
        """
        for _, module in self._instantiated_modules.items():
            try:
                module.action.stop()
            except AttributeError:  # module has new style TODO: remove_input_device statement above when moving to new style
                module.stop()

    def add_module(self, module: JOANModules, name='', parent=None, millis=100):
        """
        Add a new module
        :param module: type of module (from enum)
        :param name: name to assign to the instantiated module
        :param parent: parent of the module (mainly for the Qt-related functionality
        :param millis: module step time
        :return: module action and dialog
        """

        if not parent:
            parent = self.window

        module_action = module.action(millis=millis)
        module_dialog = module.dialog(module_action, parent=parent)

        self.window.add_module(module_dialog, module)

        # add instantiated module to dictionary
        self._instantiated_modules[module] = module_action

        return module_dialog, module_action

    def remove_module(self, module: JOANModules):
        """
        Remove module by name
        :param module: module to be removed
        """
        del self._instantiated_modules[module]

    def emergency(self):
        """
        Emergency button processing
        """
        self.stop_all()

    def quit(self):
        """
        Quit JOAN
        """
        self.stop_all()

    @property
    def instantiated_modules(self):
        return self._instantiated_modules
