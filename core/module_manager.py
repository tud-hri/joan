import os
import sys

from PyQt5 import QtCore

from core.news import News
from core.statemachine import StateMachine
from core.statesenum import State
from modules.joanmodules import JOANModules


class ModuleManager(QtCore.QObject):

    def __init__(self, module: JOANModules, time_step=0.1, parent=None):
        super(QtCore.QObject, self).__init__()

        self.module = module

        self.module_path = os.path.dirname(os.path.abspath(sys.modules[self.__class__.__module__].__file__))

        # time step
        self._time_step = time_step

        # self.singleton_status = Status()
        self.singleton_news = News()
        # self.singleton_settings = Settings()

        # initialize state machine
        self.state_machine = StateMachine(module)
        # self.state_machine.request_state_change(State.IDLE)

        self.state_machine.set_entry_action(State.IDLE, self.initialize)
        self.state_machine.set_entry_action(State.READY, self.get_ready)
        self.state_machine.set_entry_action(State.RUNNING, self.start)
        self.state_machine.set_entry_action(State.STOPPED, self.stop)
        self.state_machine.set_exit_action(State.STOPPED, self.cleanup)
        self.state_machine.set_entry_action(State.ERROR, self.stop)

        # settings
        self.settings = None

        self.shared_values = None
        self._process = None

        # create the dialog
        self.module_dialog = module.dialog(self, parent=parent)

        self.state_machine.request_state_change(State.STOPPED)

    def initialize(self):
        """
        Create shared variables, share through news
        :return:
        """
        self.shared_values = self.module.sharedvalues()

        self.singleton_news.write_news(self.module, self.shared_values)


    def get_ready(self):
        self._process = self.module.process(self.module, time_step=self._time_step, news=self.singleton_news)



    def start(self):
        # self.module_dialog.start()
        if self._process and not self._process.is_alive():
            self._process.start()


    def stop(self):
        self.module_dialog.update_timer.stop()

        # send stop state to process
        self.shared_values.state = self.state_machine.current_state.value

        # wait for the process to stop
        if self._process:
            if self._process.is_alive():
                self._process.terminate()
                print('process terminated')


    def cleanup(self):
        # TODO moeten we hier nog checken of shared values nog bestaan?
        # delete object
        # remove shared values from news
        self.singleton_news.remove_news(self.module)

        if self.shared_values:
            del self.shared_values






