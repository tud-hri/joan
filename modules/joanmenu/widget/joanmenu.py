"""JOAN menu widget"""

import os
import sys

from PyQt5 import QtCore, QtWidgets, QtGui, uic

from process import Control
from process import Status, StateHandler, MasterStates
from modules.joanmenu.action.joanmenu import JOANMenuAction


class JOANMenuWidget(Control):
    """JOAN Menu widget"""

    appisquiting = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        kwargs['callback'] = []  # method will run each given millis

        Control.__init__(self, *args, **kwargs)

        # self.status = Status({})
        # self.masterStates = self.status.masterStates
        # self.masterStateHandler = self.status.masterStateHandler
        # self.masterStateHandler.stateChanged.connect(self.handleMasterState)
        self.masterStateHandler.stateChanged.connect(self.handleMasterState)

        # create action class
        self.action = JOANMenuAction(self)

        # path to resources folder
        self._pathResources = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "resources"))
        self._pathModules = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "modules"))
        self.action.pathModules = self._pathModules

        # setup window
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('JOAN')
        self._mainWidget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "joanmenu.ui"))
        self._mainWidget.lblMasterState.setText(self.masterStateHandler.getCurrentState().name)
        self.window.setCentralWidget(self._mainWidget)
        self.window.resize(400, 400)

        self._mainWidget.btnEmergency.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._pathResources, "stop.png"))))
        self._mainWidget.btnEmergency.clicked.connect(self.emergency)

        self._mainWidget.btnQuit.setStyleSheet("background-color: darkred")
        self._mainWidget.btnQuit.clicked.connect(self.quit)

        # layout for the module groupbox
        self._layoutModules = QtWidgets.QVBoxLayout()
        self._mainWidget.grpBoxModules.setLayout(self._layoutModules)

        # add file menu
        self.fileMenu = self.window.menuBar().addMenu('File')
        self.fileMenu.addAction('Quit', self.quit)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Add module...', self.processMenuAddModule)
        self.fileMenu.addAction('Remove module...', self.processMenuRemoveModule)

    def processMenuAddModule(self):
        """Add module in menu clicked, add user-defined module"""
        moduleDirPath = QtWidgets.QFileDialog.getExistingDirectory(
            self.window, caption="Select module directory", directory=self._pathModules, options=QtWidgets.QFileDialog.ShowDirsOnly)

        # extract module folder name
        module = '%s%s' % (os.path.basename(os.path.normpath(moduleDirPath)), 'Widget')

        # add the module
        self.addModule(module)

    def addModule(self, module, name=''):
        """Instantiate module, create a widget and add to main window"""

        # instantiate module (in Action)
        instantiatedModule = self.action.addModule(module, name)
        if not instantiatedModule:
            return

        name = instantiatedModule.objectName()

        # module timer time step
        defaultMillis = 0
        try:
            defaultMillis = instantiatedModule.millis
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
        btn.clicked.connect(instantiatedModule._show)
        layout.addWidget(btn)

        # close button
        btn = QtWidgets.QPushButton("Close")
        btn.setFixedSize(80, 40)
        btn.clicked.connect(instantiatedModule._close)
        layout.addWidget(btn)

        # time step
        layout.addWidget(QtWidgets.QLabel("Time step (ms)"))
        edit = QtWidgets.QLineEdit()
        edit.textChanged.connect(instantiatedModule._setmillis)
        edit.setPlaceholderText(str(defaultMillis))
        edit.setFixedWidth(60)
        edit.setValidator(QtGui.QIntValidator(0, 2000, self))
        layout.addWidget(edit)

        # add it to the layout
        self._layoutModules.addWidget(widget)
        self.window.adjustSize()

    def processMenuRemoveModule(self):
        """User hit remove module, ask them which one to remove"""
        name, _ = QtWidgets.QInputDialog.getItem(self.window, "Select module to remove", "Modules", list(self.action.instantiatedModules.keys()))

        # remove the module in action
        self.action.removeModule(name)

        # remove the widget in the main menu
        w = self.window.centralWidget().findChild(QtWidgets.QWidget, name)
        if w is not None:
            w.setParent(None)  # this seems to work to delete the widget, removeWidget doesn't
            # self._layoutModules.removeWidget(w)  # does not work
            self.window.centralWidget().adjustSize()
            self.window.adjustSize()
            del w

    def emergency(self):
        """Emergency button processing"""
        self.masterStateHandler.requestStateChange(self.masterStates.ERROR)

    def quit(self):
        """Quit button processing"""
        reply = QtWidgets.QMessageBox.question(
            self.window, 'Quit JOAN', 'Are you sure?',
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

    def handleMasterState(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            stateAsState = self.masterStateHandler.getState(state)  # ensure we have the State object (not the int)

            self._mainWidget.lblMasterState.setText(stateAsState.name)

            # emergency stop
            if stateAsState == self.masterStates.ERROR:
                self._stop()

        except Exception as inst:
            print(inst)
