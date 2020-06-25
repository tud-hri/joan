from PyQt5 import QtCore
import time

from tools import AveragedFloat
from modules.joanmodules import JOANModules
from process.news import News
from process.settings import Settings
from process.status import Status
from process.statemachine import StateMachine


class JoanModuleAction(QtCore.QObject):
    def __init__(self, module: JOANModules, millis=100, enable_performance_monitor=True):
        # def __init__(self, module: JOANModules, master_state_handler, millis=100):
        super(QtCore.QObject, self).__init__()

        self.module_dialog = None

        self._millis = millis
        self._performance_monitor_enabled = enable_performance_monitor
        self.time_of_last_tick = time.time_ns() / 10 ** 6
        self._average_tick_time = AveragedFloat(samples=int(1000 / millis))
        self._average_run_time = AveragedFloat(samples=int(1000 / millis))

        self.module = module
        self.timer = QtCore.QTimer()
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.setInterval(millis)

        if enable_performance_monitor:
            self.timer.timeout.connect(self._do_with_performance_monitor)
        else:
            self.timer.timeout.connect(self.do)

        self.singleton_status = Status()
        self.singleton_news = News()
        self.singleton_settings = Settings()

        # initialize state machine
        self.state_machine = StateMachine(module)
        self.singleton_status.update_state_machine(module, self.state_machine)

        # initialize own data and create channel in news
        self.data = {}
        self.write_news(news=self.data)

    def _do_with_performance_monitor(self):
        self._average_tick_time.value = (time.time_ns() - self.time_of_last_tick) / 10 ** 6
        self.time_of_last_tick = time.time_ns()
        self.do()
        self._average_run_time.value = (time.time_ns() - self.time_of_last_tick) / 10 ** 6

    def do(self):
        pass

    def initialize(self):
        pass

    def start(self):
        self.timer.start()
        return True

    def stop(self):
        self.timer.stop()
        return True

    def set_millis(self, millis):
        try:
            self.millis = int(millis)
        except ValueError:
            pass

    def write_news(self, news: dict):
        """write new data to channel"""
        # assert isinstance(news, dict), 'argument "news" should be of type dict and will contain news(=data) of this channel'

        self.singleton_news.write_news(self.module, news)

    def share_settings(self, module_settings):
        """
        Shares the settings of this module with all other modules through the settings singleton.
        :param module_settings: a JoanModuleSettings child object containing this modules settings
        :return:
        """
        self.singleton_settings.update_settings(self.module, module_settings)

    def get_all_news(self):
        return self.singleton_news.all_news

    def get_available_news_channels(self):
        return self.singleton_news.all_news_keys

    def read_news(self, channel):
        return self.singleton_news.read_news(channel)

    def get_all_module_state_packages(self):
        return self.singleton_status.all_module_state_packages

    def get_available_module_state_packages(self):
        return self.singleton_status.all_module_state_package_keys

    def get_module_state_package(self, module):
        return self.singleton_status.get_module_state_package(module)

    def get_available_module_settings(self):
        return self.singleton_settings.all_settings_keys

    def get_module_settings(self, module=''):
        return self.singleton_settings.get_settings(module)

    def get_module_factory_settings(self, module=''):
        return self.singleton_settings.get_factory_settings(module)

    @property
    def millis(self):
        return self._millis

    @millis.setter
    def millis(self, val):
        if not type(val) is int:
            raise ValueError("Pulsar interval should be an integer, not " + str(type(val)))

        self._millis = val
        self.timer.setInterval(val)

    @property
    def average_tick_time(self):
        """
        :return: the average true tick time in ms
        """
        return self._average_tick_time.value

    @property
    def average_run_time(self):
        """
        :return: the average true tick time in ms
        """
        return self._average_run_time.value

    @property
    def running_frequency(self):
        try:
            return 1000 / self.average_tick_time
        except ZeroDivisionError:
            return 0.0

    @property
    def maximum_frequency(self):
        try:
            return 1000 / self.average_run_time
        except ZeroDivisionError:
            return 0.0
