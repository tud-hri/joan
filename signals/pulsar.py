import sys
from PyQt5 import QtWidgets, uic
import threading
from PyQt5 import QtCore
from time import sleep
from PyQt5 import QtGui
#from PyQt5.QtCore import pyqtSlot


import time
import traceback, sys

'''
# Using a QRunnable
# http://qt-project.org/doc/latest/qthreadpool.html
# Note that a QRunnable isn't a subclass of QObject and therefore does
# not provide signals and slots.
class Runnable(QtCore.QRunnable):

    def run(self):
        count = 0
        app = QtCore.QCoreApplication.instance()
        while count < 5:
            print("C Increasing")
            time.sleep(1)
            count += 1
        app.quit()
'''

class Pulsar(QtCore.QThread):
    """
    Gives a regular pulse from a seperate Thread
    The slots however are run in the main thread

    @param kwargs[millis] set the timer interval (default=100) in milliseconds
    """
    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)

        self.millis = 'millis' in kwargs.keys() and kwargs['millis'] or 100
        self.callback = 'callback' in kwargs.keys() and kwargs['callback'] or []
        assert type(self.millis) is int, 'millis should be an integer, now it is %r' % self.millis

        self.timer = QtCore.QTimer()
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)


    @QtCore.pyqtSlot()
    def startPulsar(self):
        for method in self.callback:
            self.timer.timeout.connect(method)
        self.timer.setInterval(self.millis)
        self.timer.start()

    @QtCore.pyqtSlot()
    def stopPulsar(self):
        # For later use
        self.timer.stop()
        try:
            self.timer.disconnect()
        except:
            pass
