import os
import sys

from PyQt5 import QtCore

from core.news import News
from core.statemachine import StateMachine
from modules.joanmodules import JOANModules


class ModuleManager(QtCore.QObject):

    def __init__(self, module: JOANModules, time_step=0.1, parent=None):
        super(QtCore.QObject, self).__init__(parent=parent)

        self.module = module

        self.module_path = os.path.dirname(os.path.abspath(sys.modules[self.__class__.__module__].__file__))

        # time step
        self._time_step = time_step

        self._shared_values = None

        # self.singleton_status = Status()
        self.singleton_news = News()
        # self.singleton_settings = Settings()

        # initialize state machine
        self.state_machine = StateMachine(module)

        # settings
        self.settings = None

        # create the dialog
        self.module_dialog = module.dialog(self, parent=parent)

    def initialize(self):
        """
        Create shared variables, share through news
        :return:
        """
        self._shared_values = self.module.sharedvalues()

        self.singleton_news.write_news(self.module, self._shared_values)

    def get_ready(self):
        self._process = self.module.process(self.module, time_step=self._time_step, news=self.singleton_news)
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def clean_up(self):
        pass
