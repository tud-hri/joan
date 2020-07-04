import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from process.joanmoduleaction import JoanModuleAction
from process.status import Status

from .performancemonitordialog import PerformanceMonitorDialog
from .settingsoverviewdialog import SettingsOverviewDialog


class JoanHQWindow(QtWidgets.QMainWindow):
    """

    """

    app_is_quiting = QtCore.pyqtSignal()

    def __init__(self, action: JoanModuleAction, parent=None):
        super().__init__(parent)

        self.action = action

        # state, statehandlers
        self.singleton_status = Status()

        # path to resources folder
        self._path_resources = os.path.normpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "resources"))
        self._path_modules = self.action.path_modules

        # setup
        self.setWindowTitle('JOAN HQ')
        self._main_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "joanhq.ui"))
        # self._main_widget.lbl_master_state.setText(self.master_state_handler.get_current_state().name)

        self.setCentralWidget(self._main_widget)
        self.resize(400, 400)

        self._main_widget.btn_emergency.setIcon(
            QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "stop.png"))))
        self._main_widget.btn_emergency.clicked.connect(self.emergency)

        self._main_widget.btn_quit.setStyleSheet("background-color: darkred")
        self._main_widget.btn_quit.clicked.connect(self.close)

        self._main_widget.btn_initialize_all.clicked.connect(self.initialize_all)

        self._main_widget.btn_stop_all.clicked.connect(self.stop_all)

        # dictionary to store all the module widgets
        self._module_cards = {}

        # add file menu
        self._file_menu = self.menuBar().addMenu('File')
        self._file_menu.addAction('Quit', self.action.quit)

        self._view_menu = self.menuBar().addMenu('View')
        self._view_menu.addAction('Show all current settings..', self.show_settings_overview)
        self._view_menu.addAction('Show performance monitor..', self.show_performance_monitor)

    def initialize_all(self):
        self.action.initialize_all()
        self._main_widget.repaint()  # repaint is essential to show the states

    def stop_all(self):
        self.action.stop_all()
        self._main_widget.repaint()  # repaint is essential to show the states

    def emergency(self):
        self.action.emergency()
        self._main_widget.repaint()  # repaint is essential to show the states

    '''
    def emergency(self):
        """ Needed here to show what is is happening in the Action-part """
        for module in JOANModules:
            module_state_machine = self.singleton_status.get_module_state_machine(module)
            if module_state_machine is not None:
                module_state_machine.request_state_change(State.IDLE)
        #self.master_state_handler.request_state_change(self.master_states.EMERGENCY)

    def initialize_all(self):
        """ Needed here to show what is is happening in the Action-part """
        for module in JOANModules:
            module_state_machine = self.singleton_status.get_module_state_machine(module)
            if module_state_machine is not None:
                module_state_machine.request_state_change(State.READY)
        #self.master_state_handler.request_state_change(self.master_states.INITIALIZING)

    def stop_all(self):
        """ Needed here to show what is is happening in the Action-part """
        for module in JOANModules:
            module_state_machine = self.singleton_status.get_module_state_machine(module)
            if module_state_machine is not None:
                module_state_machine.request_state_change(State.IDLE)
        #self.master_state_handler.request_state_change(self.master_states.STOP)
    '''

    def add_module(self, module_dialog, module_enum):
        """
        Add the module tab/UI to the modules list
        :param module_dialog:  dialog object
        :param module_enum: dialog name
        :return:
        """

        # create a widget per module (show & close buttons, state)
        name = str(module_enum)

        widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modulecard.ui"))
        widget.setObjectName(name)
        widget.grpbox.setTitle(name)

        widget.btn_showclose.clicked.connect(module_dialog.toggle_show_close)
        widget.btn_showclose.setCheckable(True)
        widget.btn_showclose.toggled.connect(lambda: self.button_showclose_checked(
            widget.btn_showclose))  # change text in the button, based toggle status
        module_dialog.closed.connect(
            lambda: widget.btn_showclose.setChecked(False))  # if the user closes the dialog, uncheck the button

        # add it to the layout
        self._main_widget.module_list_layout.addWidget(widget)
        self._main_widget.adjustSize()
        self.adjustSize()

        # with state_machine
        module_dialog.module_action.state_machine.add_state_change_listener(
            lambda: widget.lbl_state.setText(str(module_dialog.module_action.state_machine.current_state)))

        # and to the list
        self._module_cards[name] = widget

    def closeEvent(self, event):
        """
        redefine QT's closeEvent to prompt a 'Are you sure?' message box
        :param event:
        :return:
        """

        reply = QtWidgets.QMessageBox.question(
            self, 'Quit JOAN', 'Are you sure?',
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            # call our quit function
            self.action.quit()
            event.accept()
        else:
            # if we end up here, it means we didn't want to quit
            # hence, ignore the event (for Qt)
            event.ignore()

    def show_settings_overview(self):
        SettingsOverviewDialog(self.action.singleton_settings.all_settings, parent=self)

    def show_performance_monitor(self):
        PerformanceMonitorDialog(self.action._instantiated_modules, parent=self)

    def button_showclose_checked(self, button):
        if button.isChecked():
            button.setText("Close")
        else:
            button.setText("Show")
