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

        self._mainWidget.btnInitializeAll.clicked.connect(self.action.initialize)
        self._mainWidget.btnStartAll.clicked.connect(self.action.start)
        self._mainWidget.btnStopAll.clicked.connect(self.action.stop)

        # layout for the module groupbox
        self._layoutModules = QtWidgets.QVBoxLayout()
        self._mainWidget.grpBoxModules.setLayout(self._layoutModules)

        # dictionary to store all the module widgets
        self._moduleWidgets = {}

        # add file menu
        self.fileMenu = self.window.menuBar().addMenu('File')
        self.fileMenu.addAction('Quit', self.quit)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Add module...', self.processMenuAddModule)
        self.fileMenu.addAction('Rename module...', self.processMenuRenameModule)
        self.fileMenu.addAction('Remove module...', self.processMenuRemoveModule)

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

        widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modulewidget.ui"))
        widget.setObjectName(name)
        widget.grpBox.setTitle(name)

        widget.btnShow.clicked.connect(instantiatedModule._show)
        widget.btnClose.clicked.connect(instantiatedModule._close)

        widget.editTimeStepMillis.textChanged.connect(instantiatedModule._setmillis)
        widget.editTimeStepMillis.setPlaceholderText(str(defaultMillis))
        widget.editTimeStepMillis.setFixedWidth(60)
        widget.editTimeStepMillis.setValidator(QtGui.QIntValidator(0, 2000, self))
        widget.lblState.setText(instantiatedModule.moduleStateHandler.getCurrentState().name)
        instantiatedModule.moduleStateHandler.stateChanged.connect(
            lambda state: widget.lblState.setText(instantiatedModule.moduleStateHandler.getState(state).name)
        )

        # add it to the layout
        self._layoutModules.addWidget(widget)
        self.window.adjustSize()

        self._moduleWidgets[name] = widget

    def processMenuAddModule(self):
        """Add module in menu clicked, add user-defined module"""
        moduleDirPath = QtWidgets.QFileDialog.getExistingDirectory(
            self.window, caption="Select module directory", directory=self._pathModules, options=QtWidgets.QFileDialog.ShowDirsOnly)

        # extract module folder name
        module = '%s%s' % (os.path.basename(os.path.normpath(moduleDirPath)), 'Widget')

        # add the module
        self.addModule(module)

    def processMenuRemoveModule(self):
        """User hit remove module, ask them which one to remove"""
        name, _ = QtWidgets.QInputDialog.getItem(self.window, "Select module to remove", "Modules", list(self.action.instantiatedModules.keys()))

        # remove the module in action
        self.action.removeModule(name)

        # remove the widget in the main menu
        if name in self._moduleWidgets.keys():
            self._moduleWidgets[name].setParent(None)
            del self._moduleWidgets[name]
            self.window.adjustSize()
            self.window.centralWidget().adjustSize()

    def processMenuRenameModule(self):
        """Allow user to rename a widget"""

        # and create input dialog
        dlg = QtWidgets.QDialog(self.window)
        dlg.resize(QtCore.QSize(400, 100))
        dlg.setWindowTitle("Rename module")
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("Select module you want to rename"))
        cmbbox = QtWidgets.QComboBox()
        cmbbox.addItems(list(self.action.instantiatedModules.keys()))
        vbox.addWidget(cmbbox)
        vbox.addWidget(QtWidgets.QLabel("Rename to:"))
        edit = QtWidgets.QLineEdit()
        vbox.addWidget(edit)
        dlg.setLayout(vbox)
        btnbox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        btnbox.accepted.connect(dlg.accept)
        btnbox.rejected.connect(dlg.reject)
        vbox.addWidget(btnbox)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            oldName = cmbbox.currentText()
            newName = edit.text()

            # rename in instantiatedModule list
            self.action.renameModule(oldName, newName)

            # rename widget
            if oldName in self._moduleWidgets.keys():
                self._moduleWidgets[oldName].grpBox.setTitle(newName)
                self._moduleWidgets[oldName].setObjectName(newName)
                self._moduleWidgets[newName] = self._moduleWidgets.pop(oldName)

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
