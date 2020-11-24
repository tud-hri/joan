import os
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from core.module_exceptionmonitor import ModuleExceptionMonitor
from core.module_process import ProcessEvents
from core.statemachine import StateMachine
from core.statesenum import State
from modules.joanmodules import JOANModules
from core.settings import Settings
from PyQt5.QtCore import pyqtSignal, Qt


class ModuleManager(QtCore.QObject):
    loaded_signal = pyqtSignal()

    def __init__(self, module: JOANModules, news, signals, time_step_in_ms=100, parent=None):
        super(QtCore.QObject, self).__init__()

        self.module = module
        self.signals = signals

        self.module_path = os.path.dirname(os.path.abspath(sys.modules[self.__class__.__module__].__file__))

        # time step
        self._time_step_in_ms = time_step_in_ms

        self.news = news
        self.singleton_settings = Settings()

        # initialize an empty shared variables class
        self.shared_variables = self.module.shared_variables()
        self.news.write_news(self.module, self.shared_variables)

        # initialize state machine
        self.state_machine = StateMachine(module)

        self.state_machine.set_entry_action(State.INITIALIZED, self.initialize)
        self.state_machine.set_entry_action(State.READY, self.get_ready)
        self.state_machine.set_entry_action(State.RUNNING, self.start)
        self.state_machine.set_exit_action(State.RUNNING, self.stop_dialog_timer)
        self.state_machine.set_entry_action(State.STOPPED, self.stop)
        self.state_machine.set_exit_action(State.STOPPED, self.clean_up)

        self.shared_variables = None
        self._process = None
        self._events = ProcessEvents()

        self._exception_monitor = ModuleExceptionMonitor(self._events.exception, self.state_machine)

        # create the dialog
        self.module_dialog = module.dialog(self, parent=parent)

        # create settings
        self.module_settings = module.settings()

        # try to load new
        self.settings_filename = os.path.join(self.module_path, 'default_settings.json')
        if os.path.exists(self.settings_filename):
            self.load_from_file(self.settings_filename)

        self.singleton_settings.update_settings(self.module, self.module_settings)

        self.module_dialog._handle_state_change()

        self.signals.write_signal(self.module, self.loaded_signal)

        self.signals._signals[self.module].connect(self.module_dialog.update_dialog)

    def initialize(self):
        """
        Create shared variables, share through news
        The shared variable object can contain an 'adjustable setting'; which is a variable in settings that the user wants to change during RUNNING
        To make sure that the variable value is correct in shared variables, the user needs to update that variable value in shared variables after initialize()
        :return:
        """
        self.shared_variables = self.module.shared_variables()
        self.news.write_news(self.module, self.shared_variables)
        self.singleton_settings.update_settings(self.module, self.module_settings)

        # update state in shared variables
        self.shared_variables.state = self.state_machine.current_state.value



    def get_ready(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._process = self.module.process(self.module,
                                            time_step_in_ms=self._time_step_in_ms,
                                            news=self.news,
                                            settings=self.module_settings,
                                            events=self._events,
                                            settings_singleton=self.singleton_settings)

        # Start the process, run() will wait until start_event is set
        if self._process and not self._process.is_alive():
            self._process.start()

        self._events.process_is_ready.wait()

        self.shared_variables.state = self.state_machine.current_state.value
        QApplication.restoreOverrideCursor()

    def start(self):
        self.module_dialog.start()

        self._events.start.set()

        self.shared_variables.state = self.state_machine.current_state.value

    def stop(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.shared_variables.state = self.state_machine.current_state.value

        # send stop state to process and wait for the process to stop
        self.stop_dialog_timer()

        # wait for the process to stop
        if self._process:
            if self._process.is_alive():
                if not self._events.start.is_set():
                    self._events.start.set()
                self._process.join()

        print('Process terminated:', self.module)
        QApplication.restoreOverrideCursor()

    def stop_dialog_timer(self):
        self.module_dialog.update_timer.stop()

    def clean_up(self):
        # remove shared values from news
        self.news.remove_news(self.module)
        # delete object
        self.singleton_settings.remove_settings(self.module)

        # remove shared variables if any
        if self.shared_variables:
            del self.shared_variables

        self._events.start.clear()
        self._events.process_is_ready.clear()

    def load_from_file(self, settings_file_to_load):
        self.module_settings.load_from_file(settings_file_to_load)


