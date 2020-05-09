import os

from PyQt5 import QtWidgets, uic, QtGui, QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction


class JoanModuleDialog(QtWidgets.QDialog):

    # signal when dialog is closed
    closed = QtCore.pyqtSignal()

    def __init__(self, module: JOANModules, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(parent=parent)

        # reference to the action class of this module
        self.module_action = module_action

        # module and master state handling
        self.module_action.module_state_handler.state_changed.connect(self.handle_module_state)
        master_state_handler.state_changed.connect(self.handle_master_state)
        self.master_state_handler = master_state_handler

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.setWindowTitle(str(module))

        self.menu_bar = QtWidgets.QMenuBar(self)
        self.layout().setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu('File')
        self.file_menu.addAction('Close', self.close)
        self.file_menu.addSeparator()

        # setup state widget
        self.state_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/statewidget.ui"))
        self.layout().addWidget(self.state_widget)
        self.state_widget.btn_start.clicked.connect(self._button_start_clicked)
        self.state_widget.btn_stop.clicked.connect(self._button_stop_clicked)
        self.state_widget.input_tick_millis.setValidator(QtGui.QIntValidator(0, 10000, parent=self))
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.millis))
        self.state_widget.input_tick_millis.textChanged.connect(self._set_millis)

        # setup module-specific widget
        self.module_widget = uic.loadUi(module.ui_file)
        self.layout().addWidget(self.module_widget)

        # setup button enables
        self.state_widget.btn_start.setEnabled(False)

    def _button_start_clicked(self):
        self.module_action.start()
        self.state_widget.input_tick_millis.setEnabled(False)
        self.state_widget.input_tick_millis.clear()
        self.state_widget.input_tick_millis.clearFocus()
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.millis))

    def _button_stop_clicked(self):
        self.module_action.stop()
        self.state_widget.input_tick_millis.setEnabled(True)
        self.state_widget.input_tick_millis.clear()
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.millis))

    @QtCore.pyqtSlot(str)
    def _set_millis(self, millis):
        self.module_action.set_millis(millis)

    def handle_master_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        state_as_state = self.master_state_handler.get_state(state)  # ensure we have the State object (not the int)

        # update the state label
        self.state_widget.lb_module_state.setText(str(state_as_state))

    def handle_module_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        state_as_state = self.module_action.module_state_handler.get_state(state)  # ensure we have the State object (not the int)

        # update the state label
        self.state_widget.lb_module_state.setText(str(state_as_state.name))
        if state_as_state is self.module_action.module_states.EXEC.RUNNING:
            self.state_widget.lb_module_state.setStyleSheet("background: green;")
        elif state_as_state is self.module_action.module_states.EXEC.STOPPED:
            self.state_widget.lb_module_state.setStyleSheet("background: orange;")
        elif state_as_state is self.module_action.module_states.EXEC.READY:
            self.state_widget.lb_module_state.setStyleSheet("background: yellow;")
        elif 400 <= state_as_state.nr < 500:  # an Error state
            self.state_widget.lb_module_state.setStyleSheet("background: red;")

        if state_as_state == self.module_action.module_states.EXEC.READY:
            self.state_widget.btn_start.setEnabled(True)
            self.state_widget.btn_stop.setEnabled(False)
        else:
            self.state_widget.btn_start.setEnabled(False)
            self.state_widget.btn_stop.setEnabled(True)

        # If module is running change button color
        if state_as_state == self.module_action.module_states.EXEC.RUNNING:
            self.state_widget.btn_start.setStyleSheet("background-color: lightgreen")
            self.state_widget.btn_start.setText('Running')
            # self.state_widget.btn_start.setEnabled(False)
        else:
            self.state_widget.btn_start.setStyleSheet("background-color: none")
            self.state_widget.btn_start.setText('Start')
            # self.state_widget.btn_start.setEnabled(True)

    def toggle_show_close(self):
        """toggle visibility of this dialog"""
        if not self.isVisible():
            self.show()
        else:
            self.close()

    def closeEvent(self, event):
        """close event"""
        self.closed.emit()
        super().closeEvent(event)
