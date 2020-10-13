"""Action class for JOAN menu"""
import os

from PyQt5 import QtCore

from core import Settings
from modules.joanmodules import JOANModules


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
        self.path_modules = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "modules"))

        # dictionary to keep track of the instantiated modules
        self._instantiated_modules = {}

    def initialize_modules(self):
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            module.initialize()

    def start_modules(self):
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            module.start()

    def stop_modules(self):
        """
        Stop all modules
        """
        for _, module in self._instantiated_modules.items():
            module.stop()

    def add_module(self, module: JOANModules, name='', parent=None, time_step=0.1):

        if not parent:
            parent = self.window

        module_manager = module.manager(time_step=time_step)

        self.window.add_module(module_manager)

        # add instantiated module to dictionary
        self._instantiated_modules[module] = module_manager

        return module_manager

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
        self.stop_modules()

    def quit(self):
        """
        Quit JOAN
        """
        self.stop_modules()

    @property
    def instantiated_modules(self):
        return self._instantiated_modules
