"""JOAN menu widget"""

import os
import sys

from PyQt5 import QtCore, QtWidgets, QtGui, uic

from process import Control
from process import Status, StateHandler, MasterStates
from modules.joanmenu.action.joanmenu import JOANMenuAction


class JOANMenuWidget(Control):
    """JOAN Menu widget"""

    app_is_quiting = QtCore.pyqtSignal()

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
        self._path_resources = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "resources"))
        self._path_modules = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "modules"))
        self.action.path_modules = self._path_modules

        # setup window
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('JOAN')
        self._main_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "joanmenu.ui"))
        self._main_widget.lblMasterState.setText(self.masterStateHandler.getCurrentState().name)
        self.window.setCentralWidget(self._main_widget)
        self.window.resize(400, 400)

        self._main_widget.btnEmergency.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "stop.png"))))
        self._main_widget.btnEmergency.clicked.connect(self.emergency)

        self._main_widget.btnQuit.setStyleSheet("background-color: darkred")
        self._main_widget.btnQuit.clicked.connect(self.quit)

        self._main_widget.btnInitializeAll.clicked.connect(self.action.initialize)
        self._main_widget.btnStartAll.clicked.connect(self.action.start)
        self._main_widget.btnStopAll.clicked.connect(self.action.stop)

        # layout for the module groupbox
        self._layout_modules = QtWidgets.QVBoxLayout()
        self._main_widget.grpBoxModules.setLayout(self._layout_modules)

        # dictionary to store all the module widgets
        self._module_widgets = {}

        # add file menu
        self.file_menu = self.window.menuBar().addMenu('File')
        self.file_menu.addAction('Quit', self.quit)
        self.file_menu.addSeparator()
        self.file_menu.addAction('Add module...', self.process_menu_add_module)
        self.file_menu.addAction('Rename module...', self.process_menu_rename_module)
        self.file_menu.addAction('Remove module...', self.process_menu_remove_module)

    def add_module(self, module, name=''):
        """Instantiate module, create a widget and add to main window"""

        # instantiate module (in Action)
        instantiated_module = self.action.add_module(module, name)
        if not instantiated_module:
            return

        name = instantiated_module.objectName()

        # module timer time step
        default_millis = 0
        try:
            default_millis = instantiated_module.millis
        except ValueError as err:
            print("Timer tick step (millis) not defined: ", err)

        widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modulewidget.ui"))
        widget.setObjectName(name)
        widget.grpBox.setTitle(name)

        widget.btnShow.clicked.connect(instantiated_module._show)
        widget.btnClose.clicked.connect(instantiated_module._close)

        widget.editTimeStepMillis.textChanged.connect(instantiated_module._setmillis)
        widget.editTimeStepMillis.setPlaceholderText(str(default_millis))
        widget.editTimeStepMillis.setFixedWidth(60)
        widget.editTimeStepMillis.setValidator(QtGui.QIntValidator(1, 2000, self))
        widget.lblState.setText(instantiated_module.moduleStateHandler.getCurrentState().name)
        instantiated_module.moduleStateHandler.stateChanged.connect(
            lambda state: widget.lblState.setText(instantiated_module.moduleStateHandler.getState(state).name)
        )

        # add it to the layout
        self._layout_modules.addWidget(widget)
        # self._main_widget.scrollArea.adjustSize()
        self.window.adjustSize()

        self._module_widgets[name] = widget

    def process_menu_add_module(self):
        """Add module in menu clicked, add user-defined module"""
        path_module_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self.window, caption="Select module directory", directory=self._path_modules, options=QtWidgets.QFileDialog.ShowDirsOnly)

        # extract module folder name
        module = '%s%s' % (os.path.basename(os.path.normpath(path_module_dir)), 'Widget')

        # add the module
        self.add_module(module)

    def process_menu_remove_module(self):
        """User hit remove module, ask them which one to remove"""
        name, _ = QtWidgets.QInputDialog.getItem(
            self.window, "Select module to remove", "Modules", list(self.action.instantiated_modules.keys())
        )

        # remove the module in action
        self.action.remove_module(name)

        # remove the widget in the main menu
        if name in self._module_widgets.keys():
            self._module_widgets[name].setParent(None)
            del self._module_widgets[name]
            self._main_widget.grpBoxModules.adjustSize()
            self._main_widget.adjustSize()
            self.window.adjustSize()

    def process_menu_rename_module(self):
        """Allow user to rename a widget"""

        # and create input dialog
        dlg = QtWidgets.QDialog(self.window)
        dlg.resize(QtCore.QSize(400, 100))
        dlg.setWindowTitle("Rename module")
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(QtWidgets.QLabel("Select module you want to rename"))
        cmbbox = QtWidgets.QComboBox()
        cmbbox.addItems(list(self.action.instantiated_modules.keys()))
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

        # execute the dialog
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            old_name = cmbbox.currentText()
            new_name = edit.text()

            # rename in instantiated_module list
            self.action.rename_module(old_name, new_name)

            # rename widget
            if old_name in self._module_widgets.keys():
                self._module_widgets[old_name].grpBox.setTitle(new_name)
                self._module_widgets[old_name].setObjectName(new_name)
                self._module_widgets[new_name] = self._module_widgets.pop(old_name)

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
            self.app_is_quiting.emit()
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
            state_as_state = self.masterStateHandler.getState(state)  # ensure we have the State object (not the int)

            self._main_widget.lblMasterState.setText(state_as_state.name)

            # emergency stop
            if state_as_state == self.masterStates.ERROR:
                self._stop()

        except Exception as inst:
            print(inst)
