import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QSize

from core.statesenum import State
from core.status import Status
from .performancemonitordialog import PerformanceMonitorDialog
from .settingsoverviewdialog import SettingsOverviewDialog
from modules.joanmodules import JOANModules

def button_show_close_checked(button):
    if button.isChecked():
        button.setText("Close")
    else:
        button.setText("Show")


class HQWindow(QtWidgets.QMainWindow):
    app_is_quiting = QtCore.pyqtSignal()

    def __init__(self, manager, parent=None):
        super().__init__(parent)

        self.manager = manager

        # state, state handlers
        self.singleton_status = Status()

        # path to resources folder
        self._path_resources = os.path.normpath(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../", "resources"))
        self._path_modules = self.manager.path_modules

        # setup
        self.setWindowTitle('JOAN HQ')
        self._main_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/hq_window.ui"))

        self.setCentralWidget(self._main_widget)
        self.resize(400, 400)

        self._main_widget.btn_quit.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "quit.png"))))
        self._main_widget.btn_quit.setIconSize(QSize(100, 100))
        self._main_widget.btn_quit.setFixedSize(QSize(110, 110))
        self._main_widget.btn_quit.clicked.connect(self.close)

        self._main_widget.btn_initialize.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "Init.png"))))
        self._main_widget.btn_initialize.setIconSize(QSize(100,100))
        self._main_widget.btn_initialize.setFixedSize(QSize(110,110))
        self._main_widget.btn_initialize.clicked.connect(self.initialize)
        self._main_widget.btn_get_ready.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "GetReady.png"))))
        self._main_widget.btn_get_ready.setIconSize(QSize(100, 100))
        self._main_widget.btn_get_ready.setFixedSize(QSize(110, 110))
        self._main_widget.btn_get_ready.clicked.connect(self.get_ready)
        self._main_widget.btn_start.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "Run.png"))))
        self._main_widget.btn_start.setIconSize(QSize(100, 100))
        self._main_widget.btn_start.setFixedSize(QSize(110, 110))
        self._main_widget.btn_start.clicked.connect(self.start)
        self._main_widget.btn_stop.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "Stop.png"))))
        self._main_widget.btn_stop.setIconSize(QSize(100, 100))
        self._main_widget.btn_stop.setFixedSize(QSize(110, 110))
        self._main_widget.btn_stop.clicked.connect(self.stop)

        # dictionary to store all the module widgets
        self._module_cards = {}

        # add file menu
        self._file_menu = self.menuBar().addMenu('File')
        self._file_menu.addAction('Quit', self.manager.quit)

        self._view_menu = self.menuBar().addMenu('View')
        self._view_menu.addAction('Show all current settings..', self.show_settings_overview)

        self._view_menu.addAction('Show performance monitor..', self.show_performance_monitor)

    def initialize(self):
        self.manager.initialize_modules()
        self._main_widget.repaint()  # repaint is essential to show the states

    def get_ready(self):
        self.manager.get_ready_modules()
        self._main_widget.repaint()

    def start(self):
        self.manager.start_modules()
        self._main_widget.repaint()  # repaint is essential to show the states

    def stop(self):
        self.manager.stop_modules()
        self._main_widget.repaint()  # repaint is essential to show the states

    def emergency(self):
        self.manager.emergency()
        self._main_widget.repaint()  # repaint is essential to show the states

    def add_module(self, module_manager, name=''):
        """
        Add a module (in the HQ window and other widgets)
        :param module_manager: manager object
        :param name: optional
        :return:
        """
        # create a widget per module (show & close buttons, state)
        if name == '':
            name = str(module_manager.module)

        module_dialog = module_manager.module_dialog

        if module_manager.module == JOANModules.CARLA_INTERFACE:
            widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/module_card_carlainterface.ui"))
        else:
            widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/module_card.ui"))

        widget.setObjectName(name)
        widget.grpbox.setTitle(name)

        widget.btn_showclose.clicked.connect(module_dialog.toggle_show_close)
        widget.btn_showclose.setCheckable(True)
        widget.btn_showclose.toggled.connect(lambda: button_show_close_checked(widget.btn_showclose))  # change text in the button, based toggle status
        module_dialog.closed.connect(lambda: widget.btn_showclose.setChecked(False))  # if the user closes the dialog, uncheck the button

        #Attach connect and disconnect buttons for the carla interface module_card
        if module_manager.module == JOANModules.CARLA_INTERFACE:
            widget.btn_connect.setEnabled(not module_manager.connected)
            widget.btn_disconnect.setEnabled(module_manager.connected)

            widget.btn_connect.clicked.connect(module_manager.connect_carla)
            widget.btn_disconnect.clicked.connect(module_manager.disconnect_carla)

            widget.btn_connect.clicked.connect(lambda: widget.btn_connect.setEnabled(not module_manager.connected))
            widget.btn_connect.clicked.connect(lambda: widget.btn_disconnect.setEnabled(module_manager.connected))
            widget.btn_disconnect.clicked.connect(lambda: widget.btn_connect.setEnabled(not module_manager.connected))
            widget.btn_disconnect.clicked.connect(lambda: widget.btn_disconnect.setEnabled(module_manager.connected))


        # with state_machine
        try:
            module_manager.state_machine.add_state_change_listener(lambda: self.handle_state_change(widget, module_manager))
            self.handle_state_change(widget, module_dialog)

        except AttributeError:  # display nothing if the module has no state machine
            widget.lbl_state.setText(" - ")

        # add it to the layout
        self._main_widget.module_list_layout.addWidget(widget)
        self._main_widget.adjustSize()
        self.adjustSize()

        # and to the list
        self._module_cards[name] = widget
        self.handle_state_change(widget, module_manager)

    def handle_state_change(self, widget, module_manager):
        # disable all buttons first then activate the one you can press
        self.disable_all_buttons()
        current_state = module_manager.state_machine.current_state
        widget.lbl_state.setText(str(current_state))
        if current_state is State.RUNNING:
            widget.lbl_state.setStyleSheet("background: lightgreen;")
            self._main_widget.btn_stop.setEnabled(True)
        elif current_state is State.INITIALIZED:
            widget.lbl_state.setStyleSheet("background: lightblue;")
            self._main_widget.btn_get_ready.setEnabled(True)
        elif current_state is State.READY:
            widget.lbl_state.setStyleSheet("background: yellow;")
            self._main_widget.btn_start.setEnabled(True)
        elif current_state is State.ERROR:  # an Error state
            widget.lbl_state.setStyleSheet("background: red;")
            self._main_widget.btn_stop.setEnabled(True)
        elif current_state is State.STOPPED:
            widget.lbl_state.setStyleSheet("background: orange;")
            self._main_widget.btn_initialize.setEnabled(True)

    def disable_all_buttons(self):
        self._main_widget.btn_initialize.setEnabled(False)
        self._main_widget.btn_get_ready.setEnabled(False)
        self._main_widget.btn_start.setEnabled(False)
        #always be able to go back to stopped
        self._main_widget.btn_stop.setEnabled(True)

    def closeEvent(self, event):
        """
        Redefine QT's closeEvent to prompt a 'Are you sure?' message box
        :param event:
        :return:
        """
        reply = QtWidgets.QMessageBox.question(
            self, 'Quit JOAN', 'Are you sure?',
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            # call our quit function
            self.manager.quit()
            event.accept()
        else:
            # if we end up here, it means we didn't want to quit
            # hence, ignore the event (for Qt)
            event.ignore()

    def show_settings_overview(self):
        SettingsOverviewDialog(manager =self.manager, parent=self)

    def show_performance_monitor(self):
        PerformanceMonitorDialog(self.manager.instantiated_modules, parent=self)
