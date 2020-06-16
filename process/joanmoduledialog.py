import os

from PyQt5 import QtWidgets, uic, QtGui, QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.statehandler import StateHandler
from process.states import MasterStates
from process.statesenum import State
from process.status import Status

class JoanModuleDialog(QtWidgets.QDialog):

    # signal when dialog is closed
    closed = QtCore.pyqtSignal()

    def __init__(self, module: JOANModules, module_action: JoanModuleAction, parent=None):
    #def __init__(self, module: JOANModules, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(parent=parent)

        # reference to the action class of this module
        self.module_action = module_action

        # module and master state handling
        # status, statehandlers and news
        #self.singleton_status = Status()
        #self.master_state_handler = self.singleton_status._master_state_handler
        #self.master_states = self.singleton_status._master_states
        #self.master_state_handler.state_changed.connect(self.handle_master_state)

        # if module is not JOANModules.TEMPLATE:  # TODO: remove this old style
        #     self.module_action.module_state_handler.state_changed.connect(self.handle_module_state)
        # else:
        #
        self.module_action.state_machine.add_state_change_listener(self.handle_state_change)
        #self.module_action.master_state_handler.state_changed.connect(self.handle_master_state)
        #self.master_state_handler = master_state_handler

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
        self.state_widget.btn_initialize.clicked.connect(self._button_initialize_clicked)
        self.state_widget.btn_start.setEnabled(False)
        self.state_widget.btn_stop.setEnabled(False)
        self.state_widget.input_tick_millis.setValidator(QtGui.QIntValidator(0, 10000, parent=self))
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.millis))
        self.state_widget.input_tick_millis.textChanged.connect(self._set_millis)
        # reflect current state
        self.handle_state_change()

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

    def _button_initialize_clicked(self):
        self.module_action.initialize()
        self.state_widget.input_tick_millis.setEnabled(True)
        self.state_widget.input_tick_millis.clear()
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.millis))


    @QtCore.pyqtSlot(str)
    def _set_millis(self, millis):
        self.module_action.set_millis(millis)

    def handle_state_change(self):
        current_state = self.module_action.state_machine.current_state
        message = self.module_action.state_machine.state_message

        # update the state label
        self.state_widget.lbl_module_state.setText(str(current_state) + (' | ' + message if message else ''))

        if current_state is State.RUNNING:
            self.state_widget.lbl_module_state.setStyleSheet("background: green;")
        elif current_state is State.IDLE:
            self.state_widget.lbl_module_state.setStyleSheet("background: orange;")
        elif current_state is State.READY:
            self.state_widget.lbl_module_state.setStyleSheet("background: yellow;")
        elif current_state is State.ERROR:  # an Error state
            self.state_widget.lbl_module_state.setStyleSheet("background: red;")

        if current_state == State.READY:
            self.state_widget.btn_start.setEnabled(True)
        else:
            self.state_widget.btn_start.setEnabled(False)

        if current_state == State.IDLE or current_state == State.ERROR:
            self.state_widget.btn_initialize.setEnabled(True)
        else:
            self.state_widget.btn_initialize.setEnabled(False)

        if current_state == State.RUNNING:
            self.state_widget.btn_stop.setEnabled(True)
        else:
            self.state_widget.btn_stop.setEnabled(False)

        # If module is running change button color
        if current_state == State.RUNNING:
            self.state_widget.btn_start.setStyleSheet("background-color: lightgreen")
            self.state_widget.btn_start.setText('Running')
            # self.state_widget.btn_start.setEnabled(False)
        elif current_state == State.ERROR:
            self.state_widget.btn_initialize.setStyleSheet("background-color: orange")
            self.state_widget.btn_initialize.setText('Clear Error')
        else:
            self.state_widget.btn_start.setStyleSheet("background-color: none")
            self.state_widget.btn_initialize.setStyleSheet("background-color: none")
            self.state_widget.btn_initialize.setText('Initialize')
            self.state_widget.btn_start.setText('Start')
            # self.state_widget.btn_start.setEnabled(True)

    def handle_module_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        state_as_state = self.module_action.module_state_handler.get_state(state)  # ensure we have the State object (not the int)

        # update the state label
        self.state_widget.lbl_module_state.setText(str(state_as_state.name))

        if state_as_state is self.module_action.module_states.EXEC.RUNNING:
            self.state_widget.lbl_module_state.setStyleSheet("background: green;")
        elif state_as_state is self.module_action.module_states.EXEC.STOPPED:
            self.state_widget.lbl_module_state.setStyleSheet("background: orange;")
        elif state_as_state is self.module_action.module_states.EXEC.READY:
            self.state_widget.lbl_module_state.setStyleSheet("background: yellow;")
        elif 400 <= state_as_state.nr < 500:  # an Error state
            self.state_widget.lbl_module_state.setStyleSheet("background: red;")

        if state_as_state == self.module_action.module_states.EXEC.READY:
            self.state_widget.btn_start.setEnabled(True)
            self.state_widget.btn_stop.setEnabled(False)
            self.state_widget.btn_initialize.setEnabled(False)
        elif state_as_state == self.module_action.module_states.EXEC.RUNNING:
            self.state_widget.btn_start.setEnabled(False)
            self.state_widget.btn_initialize.setEnabled(False)
            self.state_widget.btn_stop.setEnabled(True)
        elif state_as_state == self.module_action.module_states.EXEC.STOPPED:
            self.state_widget.btn_start.setEnabled(False)
            self.state_widget.btn_initialize.setEnabled(True)
            self.state_widget.btn_stop.setEnabled(False)
        elif 400 <= state_as_state.nr < 500:  # an Error state
            self.state_widget.btn_start.setEnabled(False)
            self.state_widget.btn_initialize.setEnabled(True)
            self.state_widget.btn_stop.setEnabled(False)

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

            #self.module_action.module_state_handler.request_state_change(self.module_action.module_states.IDLE)
        else:
            self.close()
            #self.module_action.module_state_handler.request_state_change(self.module_action.module_states.EXEC.STOPPED)

    def closeEvent(self, event):
        """close event"""
        self.closed.emit()
        super().closeEvent(event)
