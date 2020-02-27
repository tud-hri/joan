import sys
from PyQt5 import QtWidgets, uic
import threading
from PyQt5 import QtCore
from time import sleep
from PyQt5 import QtGui
#from PyQt5.QtCore import pyqtSlot


import time
import traceback, sys

from signal import signal, SIGINT
from sys import exit

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)


# See: https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/

"""
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
"""
"""
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

        print(args, kwargs)   

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress   

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
        
"""

'''
class PulsarThread():
    def __init__(self):
        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(2)
        self.threadpool.autoDelete = True

    def start(self):
        #self.getData()
        getDataWorker = Worker(self.getData)
        #getDataWorker.autoDelete = True
        #spreadDataWorker = Worker(self.spreadData)
        getDataWorker.signals.result.connect(self.getDataResult)
        #getDataWorker.signals.progress.connect(self.pollData)

        self.threadpool.start(getDataWorker)
        #self.threadpool.start(spreadDataWorker)
        self.threadpool.waitForDone()
        #self.threadpool.clear()
        #exit(0)
'''

class Worker(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent  # = pulsar object
 
    def __del__(self):
        try:
            self.wait()   # until thread stops
            self.exit()
        except Exception as inst:
            print (inst)


    def _act(self):
        print("1_act method")
        print("2_act method")
 
    def run(self):
        self.parent(*self.args, **self.kwargs)
        #self._act()
        pass


class Pulsar(QtCore.QThread):
    """
    Gives a regular pulse in a seperate Thread
    """
    # Define signals as attributes
    trigger = QtCore.pyqtSignal()
    status = "created"

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.status = "instantiated"
        self.poll_counter = 0
        self.millis = kwargs['millis'] or 100
        self.id= kwargs['id']
        
        self.timer = QtCore.QTimer()
        #self.timer.moveToThread(self.worker)
        self.timer.timeout.connect(self.poll_data)
        self.timer.setInterval(self.millis)
        self.timer.start()
        self.status = "running"

        #self.trigger.connect(self.handle_trigger)
        #self.trigger.emit()

    def connect_trigger(self):
        # Connect a signal to a slot
        self.trigger.connect(self.handle_trigger)

        #emit the signal
        self.trigger.emit()

    #@QtCore.pyqtSlot()
    def handle_trigger(self):
        print("this slot reveived the trigger connect signal")
        #sleep(2)
        try:
            self.trigger.disconnect()
            #exit(0)
        except Exception as inst:
            print(inst) 
     
    #@QtCore.pyqtSlot()
    def poll_data(self):
        self.poll_counter += 1
        print("Polling %s %d %d id: %s" % (self.id, self.millis, self.poll_counter, self.timer.timerId()))
        if self.poll_counter == 30:
            self.timer.stop()
            try:
                self.timer.disconnect()
                if (self.timer.timerId() == -1):
                    self.status = "finished"
                    raise Exception("finished")

            except Exception as inst:
                print(inst)
    

if __name__ == '__main__':

    try:
        app = QtWidgets.QApplication(sys.argv)

        #thread1 = QtCore.QThread(Pulsar(id="2",millis=2))
        #thread2 = QtCore.QThread(Pulsar(id="1",millis=2))
        finished_counter = 0
        try:
            p1 = Pulsar(id="2",millis=200)
            p2 = Pulsar(id="1",millis=100)
        except:
            finished_counter += 1
            print ("timer thread finished")

        #    pass
        #exit(0)
        #print (thread1.currentThreadId())
        # Tell Python to run the handler() function when SIGINT is recieved
        
        #signal(SIGINT, handler)

        #print('Running. Press CTRL-C to exit.')
        #while True:
            # Do nothing and hog CPU forever until SIGINT received.
        #    pass
       
        #for i in range(0, 20):
        #    print ("p1", i, p1.status)
        #    print ("p2", i, p2.status)
        #    sleep(1)
        #exit(0)


        """
        threadpool = QtCore.QThreadPool()
        threadpool.setMaxThreadCount(2)
        threadpool.autoDelete = True

        p1 = Pulsar(id="2",millis=2)
        p2 = Pulsar(id="1",millis=1)

        threadpool.start(p1)
        threadpool.start(p2)
        threadpool.waitForDone()
        threadpool.clear()
        #exit(0)
        #p.go()
        #pt.start()
        #p.connect_trigger()
        #p.start()
        """
        #
        print(sys.exit(app.exec()))
        

    except Exception as inst:
        print(inst)
        exit(0)

