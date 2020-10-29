import multiprocessing as mp
import os
import sys

from PyQt5 import QtCore

from core.module_exceptionmonitor import ModuleExceptionMonitor
from core.module_process import ProcessEvents
from core.news import News
from core.statemachine import StateMachine
from core.statesenum import State
from core.settings import Settings
from modules.joanmodules import JOANModules
from core.settings import Settings


class ModuleManager(QtCore.QObject):

    def __init__(self, module: JOANModules, time_step_in_ms=100, parent=None):
        super(QtCore.QObject, self).__init__()

        self.module = module

        self.module_path = os.path.dirname(os.path.abspath(sys.modules[self.__class__.__module__].__file__))

        # time step
        self._time_step_in_ms = time_step_in_ms

        # self.singleton_status = Status()
        self.singleton_news = News()
        self.singleton_settings = Settings()

        # initialize state machine
        self.state_machine = StateMachine(module)
        # self.state_machine.request_state_change(State.INITIALIZED)

        self.state_machine.set_entry_action(State.INITIALIZED, self.initialize)
        self.state_machine.set_entry_action(State.READY, self.get_ready)
        self.state_machine.set_entry_action(State.RUNNING, self.start)
        self.state_machine.set_exit_action(State.RUNNING, self.stop_dialog_timer)
        self.state_machine.set_entry_action(State.STOPPED, self.stop)
        self.state_machine.set_exit_action(State.STOPPED, self.clean_up)

        self.shared_variables = None
        self._process = None
        self._events = ProcessEvents()
        # self._start_event = mp.Event()
        # self._exception_event = mp.Event()
        # self._process_is_ready_event = mp.Event()

        self._exception_monitor = ModuleExceptionMonitor(self._events.exception, self.state_machine)

        # create the dialog
        self.module_dialog = module.dialog(self, parent=parent)

        # create settings
        self.module_settings = module.settings()

        # try to load new
        settings_filename = os.path.join(self.module_path, 'default_settings.json')
        if os.path.exists(settings_filename):
            self.module_settings.load_from_file(settings_filename)

        self.singleton_settings.update_settings(self.module, self.module_settings)

        self.module_dialog._handle_state_change()

    def initialize(self):
        """
        Create shared variables, share through news
        The shared variable object can contain an 'adjustable setting'; which is a variable in settings that the user wants to change during RUNNING
        To make sure that the variable value is correct in shared variables, the user needs to update that variable value in shared variables after initialize()
        :return:
        """
        self.shared_variables = self.module.shared_variables()
        self.singleton_news.write_news(self.module, self.shared_variables)

        # update state in shared variables
        self.shared_variables.state = self.state_machine.current_state.value

        self.update_shared_variables_adjustable_settings()

    def update_shared_variables_adjustable_settings(self):
        """
        Update the adjustable settings in self.shared_variables with the current setting values
        """
        pass

    def get_ready(self):
        self._process = self.module.process(self.module,
                                            time_step_in_ms=self._time_step_in_ms,
                                            news=self.singleton_news,
                                            settings=self.module_settings,
                                            events=self._events)

        # Start the process, run() will wait until start_event is set
        if self._process and not self._process.is_alive():
            self._process.start()

        self._events.process_is_ready.wait()

        self.shared_variables.state = self.state_machine.current_state.value

    def start(self):
        self.module_dialog.start()

        self._events.start.set()

        self.shared_variables.state = self.state_machine.current_state.value

    def stop(self):
        # send stop state to process and wait for the process to stop
        self.stop_dialog_timer()

        # wait for the process to stop
        if self._process:
            if self._process.is_alive():
                self.shared_variables.state = self.state_machine.current_state.value
                self._process.join()

        print('Process terminated:', self.module)

    def stop_dialog_timer(self):
        self.module_dialog.update_timer.stop()

    def clean_up(self):

        # delete object
        # remove shared values from news
        self.singleton_news.remove_news(self.module)

        if self.shared_variables:
            del self.shared_variables

        self._events.start.clear()
        self._events.process_is_ready.clear()
