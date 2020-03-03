from widgets import MenuWidget 
from widgets import DataRecorderWidget
from widgets import InterfaceWidget
from widgets import TemplateWidget

import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from time import sleep


class WorkerSignals(QtCore.QObject):
    result = QtCore.pyqtSignal([MenuWidget], [DataRecorderWidget])

class Worker(QtCore.QRunnable):
    def __init__(self, task):
        super(Worker, self).__init__()
        self.autoDelete = True

        self.task = task
        self.signals = WorkerSignals()

    def run(self):
        print ('Sending', self.task)
        self.signals.result.emit(self.task)

class Tasks(QtCore.QObject):
    def __init__(self):
        super(Tasks, self).__init__()

        self.pool = QtCore.QThreadPool()
        #self.pool.setMaxThreadCount(4)

    @QtCore.pyqtSlot(MenuWidget)
    @QtCore.pyqtSlot(DataRecorderWidget)
    def process_result(self, task):
        print ('Receiving', task)

        task.show()

    def start(self):
        #for task in range(10):
        m = MenuWidget()
        d = DataRecorderWidget()
        tasks = (m, d)
        for task in tasks:
            worker = Worker(task)
            worker.signals.result.connect(self.process_result)

            self.pool.start(worker)
            print('active threads in the threadpool:', self.pool.activeThreadCount())

        self.pool.waitForDone()

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)

        #template = TemplateWidget()
        #template.show()
        main = Tasks()
        main.start()

        '''
        menu = MenuWidget()
        datarecorder = DataRecorderWidget()
 
        menuThread = QtCore.QThread()
        menuThread.moveToThread(menu)
        menuThread.start()
        menu.show()
    
        #dataRecorderThread = QtCore.QThread()
        #dataRecorderThread.moveToThread(datarecorder)
        #dataRecorderThread.start()
        datarecorder.show()
        '''
        print(sys.exit(app.exec()))
    except Exception as inst:
        print(inst)

