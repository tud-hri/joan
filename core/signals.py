from PyQt5 import QtCore

from modules.joanmodules import JOANModules


class Signals(QtCore.QObject):
    """
    The News class is a class that holds all the shared variables that contain the latest data
    """

    def __init__(self):
        super().__init__()
        self._signals = {}

    def write_signal(self, module: JOANModules, signal_dict):
        """
        Write data to News for a module
        :param module: used as an identifier
        :param news_dict: dictionary (keys, values) with the new data
        """
        self._signals.update({module: signal_dict})

    def read_signal(self, module: JOANModules):
        """
        Read new data from a module
        :param module:
        :return: requested data
        """
        try:
            return self._signals[module]
        except KeyError:
            return {}

    @property
    def all_signals(self):
        return self._signals
