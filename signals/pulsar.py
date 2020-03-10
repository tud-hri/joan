import sys
from PyQt5 import QtCore

import sys

class Pulsar(QtCore.QThread):
    '''
    Gives a regular pulse from a seperate Thread
    The slots however are run in the main thread

    @param kwargs[millis] set the timer interval (default=100) in milliseconds
    @param kwargs[callback] is an array of methods, coming from classes that inherit the Pulsar class
    Each method will be called on every pulse
    '''
    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)

        self.millis = 'millis' in kwargs.keys() and kwargs['millis'] or 100
        self.callback = 'callback' in kwargs.keys() and kwargs['callback'] or []
        assert type(self.millis) is int, 'millis should be an integer, now it is %r' % self.millis

        self.timer = QtCore.QTimer()
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)

    @QtCore.pyqtSlot()
    def setInterval(self, millis):
        self.millis = millis

    @QtCore.pyqtSlot()
    def startPulsar(self):
        for method in self.callback:
            try:
                # prevent connecting the same methods more than once 
                self.timer.disconnect()
            except:
                pass
            self.timer.timeout.connect(method)
        self.timer.setInterval(self.millis)
        self.timer.start()

    @QtCore.pyqtSlot()
    def stopPulsar(self):
        self.timer.stop()
        try:
            self.timer.disconnect()
        except:
            pass
