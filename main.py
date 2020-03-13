# Intantiates classes by name. The classes, however MUST already exist in globals.
# That is why classes have already been imported using a wildcard (*)
# Make sure that the requested class are also in widgets/__init__.py 
from modules import *
#from widgets import MenuWidget
#from widgets import DatarecorderWidget

from process import Status

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import sys
import traceback
import os

class Instantiate():
    '''
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)

    @param className is the class that will be instantiated
    '''
    def __init__(self, className):
        self.class_ = className in globals().keys() and globals()[className] or None
        #self.millis = millis

    def getInstantiatedClass(self):
        try:
            if self.class_:
                instantiatedClass = self.class_()
                return instantiatedClass
            else:
                print("Make sure that '%s' is lowercasename and that the class ends with 'Widget' (e.g. the widget directory 'menu' contains a class in 'menu.py' called 'MenuWidget'" % self.class_)
        except Exception as inst:
            print(inst, self.class_)
        return None


'''
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
'''
if __name__ == '__main__':

    def emergency():
        status = Status({})
        states = status.states
        statehandler = status.statehandler
        statehandler.requestStateChange(states.ERROR)
 
    try:
        app = QtWidgets.QApplication(sys.argv)
        win = QtWidgets.QWidget() #QMainWindow()
        win.resize(600, 400)

        resources = os.path.join(os.path.dirname(os.path.realpath(__file__)),'resources')
        imageName = os.path.join(resources, "stop.png")
        
        
        emergency_btn = QtWidgets.QToolButton()
        image = QtGui.QIcon(QtGui.QPixmap(imageName))
        emergency_btn.setIcon(image)

        quit_btn = QtWidgets.QPushButton('Quit')
        quit_btn.clicked.connect(app.quit)
        checkbox = QtWidgets.QCheckBox('checkbox 1')

        grid = QtWidgets.QGridLayout()
        grid.addWidget(emergency_btn, 1, 0)

        emergency_btn.setIconSize(QtCore.QSize(100,100))
        emergency_btn.clicked.connect(emergency)


        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(checkbox)
        
        grid.addLayout(layout, 1, 1)

        layout.addWidget(quit_btn)
        win.setLayout(grid)

        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'modules')

        widgetfolders = os.listdir(path)
        for widgetfolder in widgetfolders:
            if widgetfolder not in ('__pycache__', 'template', '__init__.py'):
                module = '%s%s' % (widgetfolder.title(), 'Widget')
                if module:
                    instantiated = Instantiate(module)
                    instantiatedClass = instantiated.getInstantiatedClass()
                    # get default millis which should be defined in the class that is just instantiated
                    defaultMillis = 0
                    try:
                        defaultMillis = instantiatedClass.millis
                    except:
                        pass
                    
                    # millis
                    editClass = None
                    editLabel = '%s %s' % ('Start', widgetfolder)
                    try:
                        editClass = QtWidgets.QLineEdit()
                        editClass.textChanged.connect(instantiatedClass._setmillis)
                        #editClass.setValidator()
                        editClass.setPlaceholderText(str(defaultMillis))
                        layout.addWidget(editClass)
                    except Exception as inst:
                        editLabel.__add__(' no action defined in %s' % module)
                        print(inst,"No action on button '%s', because method %s in %s does not exist" % ('editClass', '_setmillis()', module))

                    # show
                    buttonClass = None
                    buttonText = '%s %s' % ('Show', widgetfolder)
                    try:
                        buttonClass = QtWidgets.QPushButton(buttonText)
                        buttonClass.clicked.connect(instantiatedClass._show)
                        layout.addWidget(buttonClass)
                    except Exception as inst:
                        #traceback.print_exc(file=sys.stdout)
                        buttonText.__add__(' no action defined in %s' % module)
                        print(inst, "Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_show()', module))

                    # start
                    buttonClass = None
                    buttonText = '%s %s' % ('Start', widgetfolder)
                    try:
                        buttonClass = QtWidgets.QPushButton(buttonText)
                        buttonClass.clicked.connect(instantiatedClass._start)
                        layout.addWidget(buttonClass)               
                    except Exception as inst:
                        #traceback.print_exc(file=sys.stdout)
                        print(inst, "Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_start()', module))
                        #layout.removeWidget(buttonClass)
 
                    # stop
                    buttonClass = None
                    buttonText = '%s %s' % ('Stop', widgetfolder)
                    try:
                        buttonClass = QtWidgets.QPushButton(buttonText)
                        buttonClass.clicked.connect(instantiatedClass._stop)
                        layout.addWidget(buttonClass)
                    except Exception as inst:
                        buttonText.__add__(' no action defined in %s' % module)
                        print("Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_stop()', module))

                    # close widget
                    buttonClass = None
                    buttonText = '%s %s' % ('Close', widgetfolder)
                    try:
                        buttonClass = QtWidgets.QPushButton(buttonText)
                        buttonClass.clicked.connect(instantiatedClass._close)
                        layout.addWidget(buttonClass)
                    except Exception as inst:
                        buttonText.__add__(' no action defined in %s' % module)
                        print("Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_close()', module))
        win.show()

        print(sys.exit(app.exec()))
    except Exception as inst:
        traceback.print_exc(file=sys.stdout)
        print('Error:', inst)