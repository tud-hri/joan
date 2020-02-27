import sys
from PyQt5 import QtWidgets, uic
import threading
from PyQt5 import QtCore

from PyQt5 import QtGui
#from PyQt5.QtCore import pyqtSlot


import time
import traceback, sys

# See: https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/


class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress 

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


class Worker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()    

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress   
        self.kwargs['another_callback'] = 'dit dus'  
        print("kwargs in Worker", kwargs)  

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
        


class MainWindow(QtWidgets.QMainWindow):


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
    
        self.counter = 0
    
        layout = QtWidgets.QVBoxLayout()
        
        self.l = QtWidgets.QLabel("Start")
        b = QtWidgets.QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)
    
        layout.addWidget(self.l)
        layout.addWidget(b)
    
        w = QtWidgets.QWidget()
        w.setLayout(layout)
    
        self.setCentralWidget(w)
    
        self.show()

        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
    
    def progress_fn(self, n):
        print("%d%% done" % n)

    def execute_this_fn(self, progress_callback, another_callback):
        for n in range(0, 5):
            time.sleep(1)
            progress_callback.emit(n*100/4)
            
        return "Done."
 
    def print_output(self, s):
        print(s)
        
    def thread_complete(self):
        print("THREAD COMPLETE!")
 
    def oh_no(self):
        # Pass the function to execute
        worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        
        # Execute
        print(worker.autoDelete())
        self.threadpool.start(worker) 

        
    def recurring_timer(self):
        self.counter +=1
        self.l.setText("Counter: %d" % self.counter)



if __name__ == '__main__':

    try:
        app = QtWidgets.QApplication([])
        window = MainWindow()
        app.exec_()

    except Exception as inst:
        print(inst)

