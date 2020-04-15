from PyQt5 import QtWidgets, QtGui, QtCore
from modules.joanmodules import JOANModules
import abc


class JoanModuleAction:
    def __init__(self, module: JOANModules, millis=100, callbacks=None):

        self._millis = millis
        self._callbacks = callbacks if callbacks is not None else []
        self.module = module

        self.timer = QtCore.QTimer()
        self.timer.setInterval(millis)

        if callbacks is not None:
            for callback in callbacks:
                self.timer.timeout.connect(callback)

    def start_pulsar(self):
        self.timer.start()

    def stop_pulsar(self):
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

    @property
    def millis(self):
        return self._millis

    @millis.setter
    def millis(self, val):
        if not type(val) is int:
            raise ValueError("Pulsar interval should be an integer, not " + str(type(val)))

        self._millis = val
        self.timer.setInterval(val)
