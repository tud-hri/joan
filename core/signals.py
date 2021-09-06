from PyQt5 import QtCore


class Signals(QtCore.QObject):
    """
    The News class is a class that holds all the shared variables that contain the latest data
    """

    def __init__(self):
        super().__init__()
        self._signals = {}

    def write_signal(self, key, signal_dict):
        """
        Write data to News for a module
        :param key: used as an identifier
        :param signal_dict: dictionary (keys, values) with the new data
        """
        self._signals.update({key: signal_dict})

    def read_signal(self, key):
        """
        Read new data from a module
        :param key:
        :return: requested data
        """
        try:
            return self._signals[key]
        except KeyError:
            return {}

    @property
    def all_signals(self):
        return self._signals
