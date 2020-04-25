import os

from PyQt5 import QtWidgets, uic, QtGui

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction


class JoanModuleDialog(QtWidgets.QDialog):

    def __init__(self, module: JOANModules, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(parent=parent)

        # reference to the action class of this module
        self.module_action = module_action

        # module and master state handling
        self.module_action.module_state_handler.state_changed.connect(self.handle_module_state)
        master_state_handler.state_changed.connect(self.handle_master_state)
        self.master_state_handler = master_state_handler

        self.menu_bar = QtWidgets.QMenuBar(self)

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.setWindowTitle(str(module))

        # setup state widget
        self.state_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/statewidget.ui"))
        self.layout().addWidget(self.state_widget)
        self.state_widget.btn_start.clicked.connect(self._button_start_clicked)
        self.state_widget.btn_stop.clicked.connect(self._button_stop_clicked)
        self.state_widget.input_tick_millis.setValidator(QtGui.QIntValidator(0, 10000, parent=self))
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.millis))

        # setup module-specific widget
        self.module_widget = uic.loadUi(module.ui_file)
        self.layout().addWidget(self.module_widget)

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

        if state_as_state == self.module_action.module_states.TEMPLATE.RUNNING:
            self.state_widget.btn_start.setStyleSheet("background-color: green")
            self.state_widget.btn_start.setText('Running')
            self.state_widget.btn_start.setEnabled(False)
        else:
            self.state_widget.btn_start.setStyleSheet("background-color: none")
            self.state_widget.btn_start.setText('Start')
            self.state_widget.btn_start.setEnabled(True)
