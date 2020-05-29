from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.news import News
from process.settings import Settings
from process.statehandler import StateHandler
from process.states import MasterStates
from process.status import Status


class JoanModuleAction(QtCore.QObject):
    def __init__(self, module: JOANModules, millis=100):
    #def __init__(self, module: JOANModules, master_state_handler, millis=100):
        super(QtCore.QObject, self).__init__()

        self._millis = millis
        self.module = module

        self.timer = QtCore.QTimer()
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.setInterval(millis)
        self.timer.timeout.connect(self.do)

        self.singleton_status = Status()
        self.singleton_news = News()
        self.singleton_settings = Settings()

        self.module_states = module.states()
        self.module_state_handler = StateHandler(first_state=MasterStates.VOID, states_dict=self.module_states.get_states())
        module_state_package = {'module_states': self.module_states, 'module_state_handler': self.module_state_handler}

        self.singleton_status.register_module_state_package(module, module_state_package)

        # initialize own data and create channel in news
        self.data = {}
        self.write_news(news=self.data)

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
