"""Action class for JOAN menu"""
import os
import subprocess
import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

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
    signal_stop_all_modules = pyqtSignal()

    def __init__(self):
        """
        Initialize
        """
        super(QtCore.QObject, self).__init__()

        self.central_state_monitor = CentralStateMonitor()

        # Start Carla
        self.start_Carla_if_closed()

        # News
        self.news = News()

        # settings
        self.central_settings = Settings()
        self.signals = Signals()

        # path to modules directory
        self.path_modules = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../", "modules"))

        # dictionary to keep track of the instantiated modules
        self._instantiated_modules = {}

        # create window, show it
        self.window = HQWindow(self)
        self.window.show()

        # connect signals: signal_stop_all_modules, which can be called from the modules to stop all other modules
        self.signal_stop_all_modules.connect(self.stop_modules)
        self.signals.write_signal("stop_all_modules", self.signal_stop_all_modules)

    def start_Carla_if_closed(self):
        carla_status = self.check_if_carla()
        if not carla_status:
            subprocess.Popen(["C:\\Program Files\\Epic Games\\UE_4.26_forked\\Engine\\Binaries\\Win64\\UE4Editor.exe", "C:\\carla_v9.13\\Unreal\\CarlaUE4\\CarlaUE4.uproject"])
            time.sleep(10)

    def check_if_carla(self):
        process_name = "UE4Editor.exe"
        call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
        # use buildin check_output right away
        output = subprocess.check_output(call).decode()
        # check in last line for process name
        last_line = output.strip().split('\r\n')[-1]
        # because Fail message could be translated
        return last_line.lower().startswith(process_name.lower())

    def initialize_modules(self):
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            if module.use_state_machine_and_process:
                module.state_machine.request_state_change(State.INITIALIZED)

    def get_ready_modules(self):
        """
        Get all modules ready
        """
        for _, module in self._instantiated_modules.items():
            if module.use_state_machine_and_process:
                module.state_machine.request_state_change(State.READY)

    def start_modules(self):
        """
        Initialize modules
        """
        for _, module in self._instantiated_modules.items():
            if module.use_state_machine_and_process:
                module.state_machine.request_state_change(State.RUNNING)

    def stop_modules(self):
        """
        Stop all modules
        """
        for _, module in self._instantiated_modules.items():
            if module.use_state_machine_and_process:
                module.state_machine.request_state_change(State.STOPPED)

    def add_module(self, module: JOANModules, parent=None, time_step_in_ms=100):
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

        module_manager = module.manager(news=self.news, central_settings=self.central_settings, signals=self.signals,
                                        central_state_monitor=self.central_state_monitor, time_step_in_ms=time_step_in_ms, parent=parent)

        if module_manager.use_state_machine_and_process:
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
