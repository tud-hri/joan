"""Action class for JOAN menu"""
import os

from PyQt5 import QtCore

from core import News
from core import Settings
from core.hq.centralstatemonitor import CentralStateMonitor
from core.hq.hq_window import HQWindow
from core.signals import Signals
from core.statesenum import State
from modules.joanmodules import JOANModules


class HQManager(QtCore.QObject):
    """
    Action class for JoanHQ
    """

    def __init__(self):
        """
        Initialize
        """
        super(QtCore.QObject, self).__init__()

        self.central_state_monitor = CentralStateMonitor()

        # News
        self.news = News()

        # settings
        self.singleton_settings = Settings()
        self.signals = Signals()

        # path to modules directory
        self.path_modules = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../", "modules"))

        # dictionary to keep track of the instantiated modules
        self._instantiated_modules = {}

        # create window, show it
        self.window = HQWindow(self)
        self.window.show()

    def initialize_modules(self):
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            module.state_machine.request_state_change(State.INITIALIZED)

    def get_ready_modules(self):
        """
        Get all modules ready
        """
        for _, module in self._instantiated_modules.items():
            module.state_machine.request_state_change(State.READY)

    def start_modules(self):
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            module.state_machine.request_state_change(State.RUNNING)

    def stop_modules(self):
        """
        Stop all modules
        """
        for _, module in self._instantiated_modules.items():
            module.state_machine.request_state_change(State.STOPPED)

    def add_module(self, module: JOANModules, name='', parent=None, time_step_in_ms=100):
        """
        Add a module
        :param module: module type, from JOANModules enum
        :param name: optional
        :param parent: optional, if None, then self.window
        :param time_step_in_ms: self-explanatory
        :return:
        """
        if not parent:
            parent = self.window

        module_manager = module.manager(news=self.news, signals=self.signals, time_step_in_ms=time_step_in_ms, parent=parent)

        self.central_state_monitor.register_state_machine(module, module_manager.state_machine)

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

    def quit(self):
        """
        Quit JOAN
        """
        self.stop_modules()
        QtCore.QCoreApplication.quit()

    @property
    def instantiated_modules(self):
        return self._instantiated_modules
