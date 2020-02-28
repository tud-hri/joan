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
    def startTimer(self):
        for method in self.callback:
            self.timer.timeout.connect(method)
        self.timer.setInterval(self.millis)
        self.timer.start()

    @QtCore.pyqtSlot()
    def stopTimer(self):
        # For later use
        self.timer.stop()
        try:
            self.timer.disconnect()
        except:
            pass


class GetData(Pulsar):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = [self.do]
        Pulsar.__init__(self, *args, **kwargs)

    def do(self):
        print('Getting data')
        print('timerId %d' % self.timer.timerId())

'''
class Win(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    trigger = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.trigger.connect(self.go)
        self.trigger.emit()
    
    def go(self):
        pass
        self.finished.emit()
'''    

class SpreadData(Pulsar):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 10
        kwargs['callback'] = [self.do1, self.do2, self.do3]
        Pulsar.__init__(self, *args, **kwargs)

    def do1(self):
        print('1 here the data should be connected and emitted to several methods')
        print('timerId %d' % self.timer.timerId())

    def do2(self):
        '''
        objThread = QtCore.QThread()
        obj = Win()
        obj.moveToThread(objThread)
        obj.finished.connect(objThread.quit)
        objThread.started.connect(obj.trigger)
        #objThread.finished.connect(app.exit)
        objThread.start()
        '''
        print('2 here the data should be connected and emitted to several methods')

    def do3(self):
        print('3 here the data should be connected and emitted to several methods')



if __name__ == '__main__':

    trigger = QtCore.pyqtSignal()

    try:
        app = QtWidgets.QApplication(sys.argv)
        #runnable = Runnable()
        #QtCore.QThreadPool.globalInstance().start(runnable)
        win = QtWidgets.QWidget() #QMainWindow()
        win.resize(400, 300)

        start_get_btn = QtWidgets.QPushButton('Start get')
        stop_get_btn = QtWidgets.QPushButton('Stop get')
        start_spread_btn = QtWidgets.QPushButton('Start spread')
        stop_spread_btn = QtWidgets.QPushButton('Stop spread')
        quit_btn = QtWidgets.QPushButton('Quit')
        quit_btn.clicked.connect(app.quit)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(start_get_btn)
        layout.addWidget(stop_get_btn)
        layout.addWidget(start_spread_btn)
        layout.addWidget(stop_spread_btn)
        layout.addWidget(quit_btn)
        win.setLayout(layout)
        win.show()


        try:
            getData = GetData(millis=500)
            spreadData = SpreadData(millis=300)
            spreadData2 = SpreadData(millis=300)

            start_get_btn.clicked.connect(getData.startTimer)
            stop_get_btn.clicked.connect(getData.stopTimer)

            start_spread_btn.clicked.connect(spreadData.startTimer)
            stop_spread_btn.clicked.connect(spreadData.stopTimer)


        except Exception as inst:
            print('error', inst)
        print(sys.exit(app.exec()))

    except Exception as inst:
        print(inst)
        exit(0)

