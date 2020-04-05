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
        windowName = kwargs['name'] if 'name' in kwargs.keys() else ''
        self.setWindowTitle(windowName)

        # main widget
        self.mainWidget = QWidget()

        # default layout
        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)

        # file menu
        # this menu always has a close action, and allows for customized actions per module (after the close action).
        self.fileMenu = self.menuBar().addMenu('File')
        self.fileMenu.addAction('Close', self.close)
        self.fileMenu.addSeparator()

        # show menu
        # enables the user to set the visibility of all widgets loaded in the window.
        self.showMenu = self.menuBar().addMenu('Show')
        self.showMenu.triggered.connect(self.processTriggerShowMenu)

    def addWidget(self, widget, name):
        """Add widgets to the window and to the 'view' menu."""

        widget.setObjectName(name)

        # add action for each  in the view menu: this is used to show the widget
        self.showMenu.addAction(QAction(name, self.showMenu,
                                        checkable=True, checked=True))

        # and finally add the widget to the layout of the mainWidget
        self.layout.addWidget(widget)

        # adjust the size of the mainWidget and the window
        self.mainWidget.adjustSize()
        self.adjustSize()

    def processTriggerShowMenu(self, action):
        """Set visibility of the clicked widget in the view menu"""

        widget = self.mainWidget.findChild(QWidget, action.text())
        if widget is not None:
            widget.setVisible(action.isChecked())
            # adjust the size of the window
            self.mainWidget.adjustSize()
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
             