"""JOAN menu main window"""

import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from process.joanmoduleaction import JoanModuleAction
from modules.joanmodules import JOANModules


class JoanHQWindow(QtWidgets.QMainWindow):
    """Joan HQ Window"""

    app_is_quiting = QtCore.pyqtSignal()

    def __init__(self, action: JoanModuleAction, parent=None):
        super().__init__(parent)

        self.action = action
        self.master_state_handler = self.action.master_state_handler

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
        self._main_widget.btn_emergency.clicked.connect(self.action.emergency)

        self._main_widget.btn_quit.setStyleSheet("background-color: darkred")
        self._main_widget.btn_quit.clicked.connect(self.close)

        self._main_widget.btn_initialize_all.clicked.connect(self.action.initialize_all)
        self._main_widget.btn_stop_all.clicked.connect(self.action.stop_all)

        # # layout for the module groupbox
        # # TODO Dit kan mooi in de UI ook al gezet worden, zie Joris' hardwaremanager
        # self._layout_modules = QtWidgets.QVBoxLayout()
        # self._main_widget.grpbox_modules.setLayout(self._layout_modules)

        # dictionary to store all the module widgets
        self._module_cards = {}

        # add file menu
        self._file_menu = self.menuBar().addMenu('File')
        self._file_menu.addAction('Quit', self.action.quit)

    def add_module(self, module_dialog, module_enum):
        """Create a widget and add to main window"""

        # create a widget per module (show & close buttons, state)
        name = str(module_enum)

        widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modulecard.ui"))
        widget.setObjectName(name)
        widget.grpbox.setTitle(name)

        if isinstance(module_dialog, (JOANModules.FEED_BACK_CONTROLLER.dialog, JOANModules.TRAJECTORY_RECORDER.dialog)):  # syntax is changed slightly in new example: wrapping show() in _show() is unnecessary
            widget.btn_showclose.clicked.connect(module_dialog._show)
            widget.btn_showclose.setCheckable(True)
            widget.btn_showclose.toggled.connect(lambda: self.button_showclose_checked(widget.btn_showclose))

            widget.lbl_state.setText(module_dialog.module_state_handler.get_current_state().name)
            module_dialog.module_state_handler.state_changed.connect(
                lambda state: widget.lbl_state.setText(module_dialog.module_state_handler.get_state(state).name)
            )
        else:
            widget.btn_showclose.clicked.connect(module_dialog.toggle_show_close)
            widget.btn_showclose.setCheckable(True)
            widget.btn_showclose.toggled.connect(lambda: self.button_showclose_checked(widget.btn_showclose))

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