"""JOAN menu main window"""

import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
# from process.joanhq.action.joanhqaction import JoanHQAction
# from process.statehandler import StateHandler
# from process.states import MasterStates
from process.status import Status
from .performancemonitordialog import PerformanceMonitorDialog
from .settingsoverviewdialog import SettingsOverviewDialog


class JoanHQWindow(QtWidgets.QMainWindow):
    """Joan HQ Window"""

    app_is_quiting = QtCore.pyqtSignal()

    def __init__(self, action: JoanModuleAction, parent=None):
        super().__init__(parent)

        self.action = action

        # state, statehandlers
        self.singleton_status = Status()
        self.master_state_handler = self.singleton_status._master_state_handler
        self.master_states = self.singleton_status._master_states
        self.master_state_handler.state_changed.connect(self.handle_master_state)

        # path to resources folder
        self._path_resources = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "resources"))
        self._path_modules = self.action.path_modules

        # setup
        self.setWindowTitle('JOAN HQ')
        self._main_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "joanhq.ui"))
        self._main_widget.lbl_master_state.setText(self.master_state_handler.get_current_state().name)

        self.setCentralWidget(self._main_widget)
        self.resize(400, 400)

        self._main_widget.btn_emergency.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(self._path_resources, "stop.png"))))
        self._main_widget.btn_emergency.clicked.connect(self.emergency)

        self._main_widget.btn_quit.setStyleSheet("background-color: darkred")
        self._main_widget.btn_quit.clicked.connect(self.close)

        # self._main_widget.btn_initialize_all.clicked.connect(self.action.initialize_all)
        self._main_widget.btn_initialize_all.clicked.connect(self.initialize_all)
        # self._main_widget.btn_stop_all.clicked.connect(self.action.stop_all)
        self._main_widget.btn_stop_all.clicked.connect(self.stop_all)

        # # layout for the module groupbox
        # # TODO Dit kan mooi in de UI ook al gezet worden, zie Joris' hardwaremanager
        # self._layout_modules = QtWidgets.QVBoxLayout()
        # self._main_widget.grpbox_modules.setLayout(self._layout_modules)

        # dictionary to store all the module widgets
        self._module_cards = {}

        # add file menu
        self._file_menu = self.menuBar().addMenu('File')
        self._file_menu.addAction('Quit', self.action.quit)

        self._view_menu = self.menuBar().addMenu('View')
        self._view_menu.addAction('Show all current settings..', self.show_settings_overview)
        self._view_menu.addAction('Show performance monitor..', self.show_performance_monitor)

    def emergency(self):
        """ Needed here to show what is is happening in the Action-part """
        self.master_state_handler.request_state_change(self.master_states.EMERGENCY)

    def initialize_all(self):
        """ Needed here to show what is is happening in the Action-part """
        self.master_state_handler.request_state_change(self.master_states.INITIALIZING)

    def stop_all(self):
        """ Needed here to show what is is happening in the Action-part """
        self.master_state_handler.request_state_change(self.master_states.STOP)

    def handle_master_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.master_state_handler.get_state(state)  # ensure we have the State object (not the int)

            # emergency stop
            if state_as_state == self.master_states.EMERGENCY:
                self.action.stop_all()
            elif state_as_state == self.master_states.INITIALIZING:
                self.action.initialize_all()
                # self.master_state_handler.request_state_change(self.master_states.INITIALIZED)
            elif state_as_state == self.master_states.STOP:
                self.action.stop_all()
            elif state_as_state == self.master_states.QUIT:
                self.action.quit()
                # self.action.stop_all()
        except Exception as inst:
            print(inst)
        self._main_widget.lbl_master_state.setText(self.master_state_handler.get_current_state().name)

    def add_module(self, module_dialog, module_enum):
        """Create a widget and add to main window"""

        # create a widget per module (show & close buttons, state)
        name = str(module_enum)

        widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modulecard.ui"))
        widget.setObjectName(name)
        widget.grpbox.setTitle(name)

        '''
        if isinstance(module_dialog, (JOANModules.FEED_BACK_CONTROLLER.dialog)): # ,
                                      # JOANModules.TRAJECTORY_RECORDER.dialog)):  # syntax is changed slightly in new example: wrapping show() in _show() is unnecessary
            widget.btn_showclose.clicked.connect(module_dialog._show)
            widget.btn_showclose.setCheckable(True)
            widget.btn_showclose.toggled.connect(lambda: self.button_showclose_checked(widget.btn_showclose))

            widget.lbl_state.setText(module_dialog.module_state_handler.get_current_state().name)
            if module_enum is not JOANModules.TEMPLATE:
                module_dialog.module_state_handler.state_changed.connect(
                    lambda state: widget.lbl_state.setText(module_dialog.module_state_handler.get_state(state).name)
                )
            else:
                module_dialog.module_action.state_machine.add_state_change_listener(
                    lambda: widget.lbl_state.setText(str(module_dialog.module_action.state_machine.current_state)))
        else:
        '''
        widget.btn_showclose.clicked.connect(module_dialog.toggle_show_close)
        widget.btn_showclose.setCheckable(True)
        widget.btn_showclose.toggled.connect(lambda: self.button_showclose_checked(widget.btn_showclose))  # change text in the button, based toggle status
        module_dialog.closed.connect(lambda: widget.btn_showclose.setChecked(False))  # if the user closes the dialog, uncheck the button

        if not isinstance(module_dialog, (JOANModules.TEMPLATE.dialog)):
            module_dialog.module_action.module_state_handler.state_changed.connect(
                lambda state: widget.lbl_state.setText(module_dialog.module_action.module_state_handler.get_state(state).name)
            )

        # add it to the layout
        self._main_widget.module_list_layout.addWidget(widget)
        self._main_widget.adjustSize()
        self.adjustSize()

        # and to the list
        self._module_cards[name] = widget

    def closeEvent(self, event):
        """redefined closeEvent"""

        """Quit button processing"""
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
        """change the text of the module card's show/close button"""
        if button.isChecked():
            button.setText("Close")
        else:
            button.setText("Show")

    # def process_menu_add_module(self):
    #     """Add module in menu clicked, add user-defined module"""
    #     path_module_dir = QtWidgets.QFileDialog.getExistingDirectory(
    #         self, caption="Select module directory", directory=self._path_modules, options=QtWidgets.QFileDialog.ShowDirsOnly
    #     )

    #     # extract module folder name
    #     module = '%s%s' % (os.path.basename(os.path.normpath(path_module_dir)), 'Widget')

    #     # add the module
    #     self.add_module(module)

    # def process_menu_remove_module(self):
    #     """User hit remove module, ask them which one to remove"""
    #     name, _ = QtWidgets.QInputDialog.getItem(
    #         self.window, "Select module to remove", "Modules", list(self.action.instantiated_modules.keys())
    #     )

    #     # remove the module in action
    #     self.action.remove_module(name)

    #     # remove the widget in the main menu
    #     if name in self._module_cards.keys():
    #         self._module_cards[name].setParent(None)  # setting parent to None destroys the widget (garbage collector)
    #         del self._module_cards[name]
    #         # adjust size
    #         self._main_widget.grpBoxModules.adjustSize()
    #         self._main_widget.adjustSize()
    #         self.adjustSize()
