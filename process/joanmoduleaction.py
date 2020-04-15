from PyQt5 import QtWidgets, QtGui, QtCore
from modules.joanmodules import JOANModules
from process.control import Status, News
from process.states import MasterStates
from process.statehandler import StateHandler
import abc


class JoanModuleAction(QtCore.QObject):
    def __init__(self, module: JOANModules, master_state_handler, millis=100, callbacks=None):
        super().__init__()

        self._millis = millis
        self._callbacks = callbacks if callbacks is not None else []
        self.module = module

        self.timer = QtCore.QTimer()
        self.timer.setInterval(millis)

        self.singleton_status = Status({})
        self.singleton_news = News({})

        # initialize states and state handler
        self.moduleStates = module.states()
        self.moduleStateHandler = StateHandler(firstState=MasterStates.VOID, statesDict=self.moduleStates.getStates())
        module_state_package = {'moduleStates': self.moduleStates, 'moduleStateHandler': self.moduleStateHandler}
        self.singleton_status = Status({module: module_state_package})

        # initialize own data and create channel in news
        self.data = {}
        self.write_news(news=self.data)

        if callbacks is not None:
            for callback in callbacks:
                self.timer.timeout.connect(callback)

        self.moduleStateHandler.stateChanged.connect(self.handle_module_state)
        master_state_handler.stateChanged.connect(self.handle_master_state)

    def do(self):
        pass

    def initialize(self):
        pass

    def start(self):
        self._start_pulsar()
        return True

    def stop(self):
        self._stop_pulsar()
        return True

    def _start_pulsar(self):
        self.timer.start()

    def _stop_pulsar(self):
        self.timer.stop()

    def add_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
            self.timer.timeout.connect(callback)
        else:
            print("Warning in " + str(self.module) + ", attempted to add callback that was already registered. Request was ignored.")

    def remove_callback(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

            # TODO: keep track of connections and only disconnect the specific callback
            self.timer.disconnect()
            for callback in self._callbacks:
                self.timer.timeout.connect(callback)

        else:
            print("Warning in " + str(self.module) + ", attempted to remove unknown callback. Request was ignored.")

    def handle_master_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        state_as_state = self.masterStateHandler.getState(state)  # ensure we have the State object (not the int)
        # emergency stop
        if state_as_state == self.moduleStates.ERROR:
            self.module_action.stop_pulsar()

    def handle_module_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        state_as_state = self.moduleStateHandler.getState(state)  # ensure we have the State object (not the int)
        # emergency stop
        if state_as_state == self.moduleStates.ERROR:
            self.stop_pulsar()

    def write_news(self, news: dict):
        """write new data to channel"""
        assert type(news) == dict, 'argument "news" should be of type dict and will contain news(=data) of this channel'

        self.singleton_news = News({self.module: news})

    def get_all_news(self):
        return self.singleton_news.news

    def get_available_news_channels(self):
        return self.singleton_news.news.keys()

    def read_news(self, channel):
        try:
            return self.singleton_news.news[channel]
        except KeyError:
            return {}

    def get_all_module_state_packages(self):
        return self.singleton_status.moduleStatePackages

    def get_available_module_state_packages(self):
        return self.singleton_status.moduleStatePackages.keys()

    def get_module_state_package(self, module):
        try:
            return self.singleton_status.moduleStatePackages[module]
        except KeyError:
            return {}

    @property
    def millis(self):
        return self._millis

    @millis.setter
    def millis(self, val):
        if not type(val) is int:
            raise ValueError("Pulsar interval should be an integer, not " + str(type(val)))

        self._millis = val
        self.timer.setInterval(val)
