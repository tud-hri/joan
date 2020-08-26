import os
import sys
import time

from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmodulesignals import JoanModuleSignal
from process.news import News
from process.settings import Settings
from process.signals import Signals
from process.statemachine import StateMachine
from process.status import Status
from tools import AveragedFloat


class JoanModuleAction(QtCore.QObject):

    def __init__(self, module: JOANModules, millis=100, enable_performance_monitor=True,
                 use_state_machine_and_timer=True):
        """
        Initialize
        :param module: module type
        :param millis: module time step
        :param enable_performance_monitor: self-explanatory
        """
        super(QtCore.QObject, self).__init__()

        self.module_dialog = None

        self._millis = millis
        self._performance_monitor_enabled = enable_performance_monitor
        self._use_state_machine_and_timer = use_state_machine_and_timer
        self.time_of_last_tick = time.time_ns() / 10 ** 6
        self._average_tick_time = AveragedFloat(samples=int(1000 / millis))
        self._average_run_time = AveragedFloat(samples=int(1000 / millis))

        self.module = module

        self.module_path = os.path.dirname(os.path.abspath(sys.modules[self.__class__.__module__].__file__)).strip('action')

        self.singleton_status = Status()
        self.singleton_news = News()
        self.singleton_settings = Settings()
        self.singleton_signals = Signals()

        if use_state_machine_and_timer:
            self.timer = QtCore.QTimer()
            self.timer.setTimerType(QtCore.Qt.PreciseTimer)
            self.timer.setInterval(millis)

            if enable_performance_monitor:
                self.timer.timeout.connect(self._do_with_performance_monitor)
            else:
                self.timer.timeout.connect(self.do)

        # initialize state machine
        self.state_machine = StateMachine(module)
        self.singleton_status.update_state_machine(module, self.state_machine)

        # initialize own data and create channel in news
        self.data = {}
        self.write_news(news=self.data)

        # settings
        self.settings = None

        # (py)Qt signals for triggering specific module actions/functions
        # these signals are all stored in a JoanModuleSignal class; add them there if you need more signals.
        self._module_signals = JoanModuleSignal(module, self)
        self.singleton_signals.add_signals(self.module, self._module_signals)

    def register_module_dialog(self, module_dialog):
        self.module_dialog = module_dialog

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
        if self._use_state_machine_and_timer:
            self.timer.start()
            return True
        else:
            return False

    def stop(self):
        if self._use_state_machine_and_timer:
            self.timer.stop()
            return True
        else:
            return False

    def write_news(self, news: dict):
        """
        Write new data to channel
        """
        self.singleton_news.write_news(self.module, news)

    def read_news(self, channel):
        return self.singleton_news.read_news(channel)

    def get_all_news(self):
        return self.singleton_news.all_news

    def get_available_news_channels(self):
        return self.singleton_news.all_news_keys

    def share_settings(self, module_settings):
        """
        Shares the settings of this module with all other modules through the settings singleton.
        :param module_settings: a JoanModuleSettings child object containing this modules settings
        """
        self.singleton_settings.update_settings(self.module, module_settings)

    def load_default_settings(self):
        # load existing settings
        default_settings_file_location = os.path.join(self.module_path, 'action', 'default_settings.json')

        if os.path.isfile(default_settings_file_location):
            self.settings.load_from_file(default_settings_file_location)

    def prepare_load_settings(self):
        """Override this function if you need to prepare your module before the new settings are loaded"""
        pass

    def apply_loaded_settings(self):
        """Apply the new settings once these are loaded"""
        pass

    def load_settings_from_file(self, settings_file_to_load):
        """
        Loads appropriate settings from .json file
        :param settings_file_to_load:
        :return:
        """
        self.settings.load_from_file(settings_file_to_load)
        self.share_settings(self.settings)

    def save_settings_to_file(self, file_to_save_in):
        """
        Saves current settings to json file
        :param file_to_save_in:
        :return:
        """
        self.settings.save_to_file(file_to_save_in)

    def get_available_module_settings(self):
        return self.singleton_settings.all_settings_keys

    def get_module_settings(self, module=''):
        return self.singleton_settings.get_settings(module)

    def get_module_factory_settings(self, module=''):
        return self.singleton_settings.get_factory_settings(module)

    @property
    def tick_interval_ms(self):
        return self._millis

    @tick_interval_ms.setter
    def tick_interval_ms(self, val):
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
