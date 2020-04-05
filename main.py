"""Main script
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)
    Make sure that the requested class are also in widgets/__init__.py 
"""

import sys
import traceback
import os
# import qdarkgraystyle

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic

from modules import DatarecorderWidget, SiminterfaceWidget
from process import Status
from process import MasterStates


class Instantiate():
    """"
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)

    @param className is the class that will be instantiated
    """

    def __init__(self, className):
        self._class = className in globals().keys() and globals()[className] or None

    def getInstantiatedClass(self):
        try:
            if self._class:
                return self._class()
            else:
                print("Make sure that '%s' is lowercasename and that the class ends with 'Widget' (e.g. the widget directory 'menu' contains a class in 'menu.py' called 'MenuWidget'" % self._class)
        except Exception as inst:
            traceback.print_exc(file=sys.stdout)
            print(inst, self._class)

        return None


class JOANWindow(QtWidgets.QMainWindow):
    appisquiting = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__()

        resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

        self.setWindowTitle('JOAN')
        mainWidget = uic.loadUi(os.path.join(resources, "menuwidget.ui"))
        self.setCentralWidget(mainWidget)
        self.resize(400, 400)

        mainWidget.btnEmergency.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(resources, "stop.png"))))
        mainWidget.btnEmergency.clicked.connect(self.emergency)

        mainWidget.btnQuit.setStyleSheet("background-color: darkred")
        mainWidget.btnQuit.clicked.connect(self.quit)

        self._layoutModules = QtWidgets.QVBoxLayout()
        mainWidget.grpBoxModules.setLayout(self._layoutModules)

        self.show()

    def addModule(self, module):

        # instantiate module
        instantiated = Instantiate(module)
        instantiatedClass = instantiated.getInstantiatedClass()

        # module timer time step
        defaultMillis = 0
        try:
            defaultMillis = instantiatedClass.millis
        except:
            pass

        # create a module widget
        widget = QtWidgets.QWidget()
        widget.setObjectName(str(module))
        layout = QtWidgets.QHBoxLayout()
        widget.setLayout(layout)

        # label with name
        label = QtWidgets.QLabel(str(module).replace("Widget", ""))
        label.setMinimumWidth(100)
        label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        layout.addWidget(label)

        # show button
        btn = QtWidgets.QPushButton("Show")
        btn.setFixedSize(80, 40)
        btn.clicked.connect(instantiatedClass._show)
        layout.addWidget(btn)

        # close button
        btn = QtWidgets.QPushButton("Close")
        btn.setFixedSize(80, 40)
        btn.clicked.connect(instantiatedClass._close)
        layout.addWidget(btn)

        # time step
        layout.addWidget(QtWidgets.QLabel("Time step (ms)"))
        edit = QtWidgets.QLineEdit()
        edit.textChanged.connect(instantiatedClass._setmillis)
        edit.setPlaceholderText(str(defaultMillis))
        edit.setFixedWidth(60)
        edit.setValidator(QtGui.QIntValidator(0, 2000, self))
        layout.addWidget(edit)

        # add it to the layout
        self._layoutModules.addWidget(widget)
        self.adjustSize()

    def emergency(self):
        """Emergency button processing"""
        status = Status({})
        masterStateHandler = status.masterStateHandler
        masterStateHandler.requestStateChange(MasterStates.ERROR)

    def quit(self):
        """Quit button processing"""
        reply = QtWidgets.QMessageBox.question(
            self, 'Quit JOAN', 'Are you sure?',
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.appisquiting.emit()
            sys.exit()

    def closeEvent(self, event):
        """redefined closeEvent"""
        # call our quit function
        self.quit()

        # if we end up here, it means we didn't want to quit
        # hence, ignore the event (for Qt)
        event.ignore()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    window = JOANWindow()
    window.show()
    window.addModule('DatarecorderWidget')
    window.addModule('SiminterfaceWidget')

    widgetfolders = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modules"))
    for widgetfolder in widgetfolders:
        if widgetfolder not in ('__pycache__', 'interface', 'template', 'menu', '__init__.py'):
            module = '%s%s' % (widgetfolder.title(), 'Widget')
            print(module)

    app.exec_()



        # widgetfolders = os.listdir(path)
        # for widgetfolder in widgetfolders:
        #     #if widgetfolder not in ('__pycache__', 'template', '__init__.py'):
        #     if widgetfolder not in ('__pycache__', 'interface', 'template', 'menu', '__init__.py'):
        #         module = '%s%s' % (widgetfolder.title(), 'Widget')
        #         if module:
        #             instantiated = Instantiate(module)
        #             instantiatedClass = instantiated.getInstantiatedClass()
        #             # get default millis which should be defined in the class that is just instantiated
        #             defaultMillis = 0
        #             try:
        #                 defaultMillis = instantiatedClass.millis
        #             except:
        #                 pass
                    
        #             # millis
        #             editClass = None
        #             editLabel = '%s %s' % ('Start', widgetfolder)
        #             # try:
        #             #     editClass = QtWidgets.QLineEdit()
        #             #     editClass.textChanged.connect(instantiatedClass._setmillis)
        #             #     #editClass.setValidator()
        #             #     editClass.setPlaceholderText(str(defaultMillis))
        #             #     layout.addWidget(editClass)
        #             # except Exception as inst:
        #             #     editLabel.__add__(' no action defined in %s' % module)
        #             #     print(inst,"No action on button '%s', because method %s in %s does not exist" % ('editClass', '_setmillis()', module))

        #             # show
        #             buttonClass = None
        #             buttonText = '%s %s' % ('Show', widgetfolder)
        #             try:
        #                 buttonClass = QtWidgets.QPushButton(buttonText)
        #                 buttonClass.clicked.connect(instantiatedClass._show)
        #                 layout.addWidget(buttonClass)
        #             except Exception as inst:
        #                 #traceback.print_exc(file=sys.stdout)
        #                 buttonText.__add__(' no action defined in %s' % module)
        #                 print(inst, "Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_show()', module))

        #             # start
        #             buttonClass = None
        #             buttonText = '%s %s' % ('Start', widgetfolder)
        #             try:
        #                 buttonClass = QtWidgets.QPushButton(buttonText)
        #                 buttonClass.clicked.connect(instantiatedClass._start)
        #                 layout.addWidget(buttonClass)               
        #             except Exception as inst:
        #                 #traceback.print_exc(file=sys.stdout)
        #                 print(inst, "Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_start()', module))
        #                 #layout.removeWidget(buttonClass)
 
        #             # stop
        #             buttonClass = None
        #             buttonText = '%s %s' % ('Stop', widgetfolder)
        #             try:
        #                 buttonClass = QtWidgets.QPushButton(buttonText)
        #                 buttonClass.clicked.connect(instantiatedClass._stop)
        #                 layout.addWidget(buttonClass)
        #             except Exception as inst:
        #                 buttonText.__add__(' no action defined in %s' % module)
        #                 print("Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_stop()', module))

        #             # close widget
        #             buttonClass = None
        #             buttonText = '%s %s' % ('Close', widgetfolder)
        #             try:
        #                 buttonClass = QtWidgets.QPushButton(buttonText)
        #                 buttonClass.clicked.connect(instantiatedClass._close)
        #                 layout.addWidget(buttonClass)
        #             except Exception as inst:
        #                 buttonText.__add__(' no action defined in %s' % module)
        #                 print("Warning: No action on button '%s', because method %s in %s does not exist" % (buttonText, '_close()', module))
        
        # layout.addWidget(quit_btn)
    #     win.show()


    #     print(sys.exit(app.exec()))
    # except Exception as inst:
    #     traceback.print_exc(file=sys.stdout)
    #     print('Error:', inst) 