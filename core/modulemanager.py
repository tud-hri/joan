import os
import sys
import time

from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from core.joanmodulesignals import JoanModuleSignal
from core.news import News
from core.settings import Settings
from core.signals import Signals
from core.statemachine import StateMachine
from core.status import Status
from tools import AveragedFloat


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

        self.singleton_news.write_news(self.module, {'sv': self._shared_values})

        print(self.singleton_news)

        pass

    def get_ready(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def clean_up(self):
        pass
