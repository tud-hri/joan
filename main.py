"""Main script
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)
    Make sure that the requested class are also in widgets/__init__.py 
"""

import sys
import inspect
import traceback
import os
# import qdarkgraystyle

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic

from modules import *
from process import Status
from process import MasterStates


class Instantiate():
    """"
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)

    @param className is the class that will be instantiated
    """

    def __init__(self, className):
        self._class = globals()[className] if className in globals().keys() else None

    def getInstantiatedClass(self):
        """Return instantiated class"""
        try:
            if self._class:
                return self._class()
            else:
                print("Make sure that '%s' is lowercasename and that the class ends with 'Widget'" % self._class)
                return None
        except NameError as inst:
            traceback.print_exc(file=sys.stdout)
            print(inst, self._class)

        return None


class JOANAppMainWindow(QtWidgets.QMainWindow):
    """ Creates the main JOAN window and allows adding modules
        Contains the the masterstate handler
    """
    appisquiting = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        resources = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

        # setup window
        self.setWindowTitle('JOAN')
        mainWidget = uic.loadUi(os.path.join(resources, "menuwidget.ui"))
        self.setCentralWidget(mainWidget)
        self.resize(400, 400)

        mainWidget.btnEmergency.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(resources, "stop.png"))))
        mainWidget.btnEmergency.clicked.connect(self.emergency)

        mainWidget.btnQuit.setStyleSheet("background-color: darkred")
        mainWidget.btnQuit.clicked.connect(self.quit)

        # layout for the module groupbox
        self._layoutModules = QtWidgets.QVBoxLayout()
        mainWidget.grpBoxModules.setLayout(self._layoutModules)

        # add file menu
        self.fileMenu = self.menuBar().addMenu('File')
        self.fileMenu.addAction('Quit', self.quit)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Add module...', self.processMenuAddModule)
        self.fileMenu.addAction('Remove module...', self.processMenuRemoveModule)

        # dictionary to keep track of the instantiated modules
        self._instantiatedModules = {}

    def addModule(self, module, name=''):
        """Instantiate module, create a widget and add to main window"""

        # if name is not given, take str(module)
        if name == '':
            name = str(module)

        # check if this name is already taken
        if name in self._instantiatedModules.keys():
            # key exists, prompt user to give a new name

            # first, find new name (appending counter)
            counter = 1
            newName = '%s-%d' % (name, counter)
            while newName in self._instantiatedModules.keys():
                newName = '%s-%d' % (name, counter+1)

            # and create input dialog
            name, _ = QtWidgets.QInputDialog.getText(self, "Get text", "Your name:", QtWidgets.QLineEdit.Normal, newName)

        # instantiate class module
        instantiated = Instantiate(module)
        instantiatedClass = instantiated.getInstantiatedClass()

        # raise typeerror if module/instantiatedClass is None
        if instantiatedClass is None:
            print("Cannot instantiate class ", module)
            return

        # add instantiated modules to dictionary
        self._instantiatedModules[name] = instantiatedClass

        # module timer time step
        defaultMillis = 0
        try:
            defaultMillis = instantiatedClass.millis
        except ValueError as e:
            print("Timer tick step (millis) not defined: ", e)

        # create a module widget
        widget = QtWidgets.QWidget()
        widget.setObjectName(name)
        layout = QtWidgets.QHBoxLayout()
        widget.setLayout(layout)

        # label with name
        label = QtWidgets.QLabel(name.replace("Widget", ""))
        label.setMinimumWidth(150)
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

    def removeModule(self, name):
        """ Remove module by name"""

        # remove the widget in the main menu
        w = self.centralWidget().findChild(QtWidgets.QWidget, name)
        if w is not None:
            w.setParent(None)  # this seems to work to delete the widget, removeWidget doesn't
            # self._layoutModules.removeWidget(w)  # does not work
            self.centralWidget().adjustSize()
            self.adjustSize()
            del w

        del self._instantiatedModules[name]

    def processMenuAddModule(self):
        """Add module in menu clicked, add user-defined module"""
        modulePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules')
        moduleDirPath = QtWidgets.QFileDialog.getExistingDirectory(
            self, caption="Select module directory", directory=modulePath, options=QtWidgets.QFileDialog.ShowDirsOnly)

        # extract module folder name
        module = '%s%s' % (os.path.basename(os.path.normpath(moduleDirPath)), 'Widget')

        # check if a class with the name 'module' is present in the live objects of this module.
        # if so, make sure it matches (case etc)
        # this assumes that the module is imported through the wildcard
        # through: from modules import *
        clsmembers = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))
        foundClass = False
        for key, _ in clsmembers.items():
            if key.lower() == module.lower():
                module = key
                foundClass = True

        if foundClass is False:
            print("Module class not found. The module needs to be in its own folder in the 'modules' folder.")
            return

        # add the module
        self.addModule(module)

    def processMenuRemoveModule(self):
        """User hit remove module, ask them which one to remove"""
        name, _ = QtWidgets.QInputDialog.getItem(self, "Select module to remove", "Modules", list(self._instantiatedModules.keys()))

        self.removeModule(name)

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

    APP = QtWidgets.QApplication(sys.argv)

    WINDOW = JOANAppMainWindow()
    WINDOW.show()

    # adding modules (instantiates them too)
    WINDOW.addModule('DatarecorderWidget')

    # # printing widget folders
    # WIDGETFOLDERS = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modules"))
    # for widgetfolder in WIDGETFOLDERS:
    #     if widgetfolder not in ('__pycache__', 'interface', 'template', 'menu', '__init__.py'):
    #         module = '%s%s' % (widgetfolder.title(), 'Widget')
    #         print(module)

    APP.exec_()
