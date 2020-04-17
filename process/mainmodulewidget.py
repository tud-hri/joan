"""Module widget class"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox, QVBoxLayout, QAction


class MainModuleWidget(QMainWindow):
    """ QWidget for module widgets

        Implements a QMainWindow in which all widgets for a menu can be loaded.
        We include a general state widget and allow for a module-specific widget
    """

    # closed signal (when mainwindow is closed)
    closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__()

        self._showClosePrompt = kwargs['showcloseprompt'] if 'showcloseprompt' in kwargs.keys() else False
        window_name = kwargs['name'] if 'name' in kwargs.keys() else ''
        self.setWindowTitle(window_name)

        # main widget
        self.main_widget = QWidget()

        # default layout
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        # file menu
        # this menu always has a close action, and allows for customized actions per module (after the close action).
        self.file_menu = self.menuBar().addMenu('File')
        self.file_menu.addAction('Close', self.close)
        self.file_menu.addSeparator()

        # show menu
        # enables the user to set the visibility of all widgets loaded in the window.
        self.show_menu = self.menuBar().addMenu('Show')
        self.show_menu.triggered.connect(self.processTriggerShowMenu)

    def addWidget(self, widget, name):
        """Add widgets to the window and to the 'view' menu."""

        widget.setObjectName(name)

        # add action for each  in the view menu: this is used to show the widget
        self.show_menu.addAction(QAction(name, self.show_menu,
                                        checkable=True, checked=True))

        # and finally add the widget to the layout of the main_widget
        self.layout.addWidget(widget)

        # adjust the size of the main_widget and the window
        self.main_widget.adjustSize()
        self.adjustSize()

    def processTriggerShowMenu(self, action):
        """Set visibility of the clicked widget in the view menu"""

        widget = self.main_widget.findChild(QWidget, action.text())
        if widget is not None:
            widget.setVisible(action.isChecked())
            # adjust the size of the window
            self.main_widget.adjustSize()
            self.adjustSize()

    def closeEvent(self, event):
        """redefined closeEvent, emits closed signal"""

        if self.isVisible():

            if self._showClosePrompt:
                reply = QMessageBox.question(
                    self, 'Close window', 'Are you sure?',
                    QMessageBox.Yes, QMessageBox.No
                )

                if reply == QMessageBox.No:
                    event.ignore()
                    return

            # window is closed, emit closed signal and accept the event
            self.closed.emit()
            event.accept()
