from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui


class MainModuleWidget(QtWidgets.QMainWindow):

    # closed signal (when mainwindow is closed)
    closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__()

        # main widget
        self.mainWidget = QtWidgets.QWidget()

        # default layout
        self.layout = QtWidgets.QVBoxLayout()
        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)
        
        # file menu
        # this menu always has a close action, and allows for customized actions per module (after the close action). 
        # Examples would be to store the settings of the moduel
        self.fileMenu = self.menuBar().addMenu('File')
        self.fileMenu.addAction('Close', self.close) # add action and directly connect function to it (this case close, can be any user-defined function)
        self.fileMenu.addSeparator()

        # show menu
        # Enables the user to set the visibility of all widgets loaded in the window.
        self.showMenu = self.menuBar().addMenu('Show')
        self.showMenu.triggered.connect(self.processTriggerShowMenu)
        
        # self.askConfirmClose = 'askCloseConfirm' in kwargs.keys() and kwargs['askCloseConfirm'] or False
        # self.showStateWidget = 'showStateWidget' in kwargs.keys() and kwargs['showStateWidget'] or False

    def addWidget(self, widget, name='widget'):
        ''' addWidget 
        We assign a name to the widget ('widget' by default or finds an unique one by appending a counter)
        and adds the widget to the mainWidget (the window's centralWidget).
        We also automatically add the widget to the 'showMenu'.
        '''

        # if the default name is given, check if it already exists in the central Widget, and add counter
        if self.mainWidget.findChild(QtWidgets.QWidget, name) is not None:
            for i in range(len(self.mainWidget.findChildren(QtWidgets.QWidget))):
                tmpname = name + '-' + str(i)
                if self.mainWidget.findChild(QtWidgets.QWidget, tmpname) is None:
                    name = tmpname
                    break

        # set widget name
        widget.setObjectName(name)

        # add action for each  in the view menu: this is used to show the widget
        self.showMenu.addAction(QtWidgets.QAction(name, self.showMenu, checkable=True, checked=True))

        # and finally add the widget to the layout of the mainWidget
        self.layout.addWidget(widget)

    def processTriggerShowMenu(self, action):
        '''
        Using action.text(), you can process the action that is triggered in the show menu (check/uncheck of widget visibility). Find the widget based on name, and toggle its visibility
        '''
        widget = self.mainWidget.findChild(QtWidgets.QWidget, action.text())
        if widget is not None:
            widget.setVisible(action.isChecked())
            # adjust the size of the window
            self.mainWidget.adjustSize()
            self.adjustSize()

    def closeEvent(self, event):

        # reply = QtGui.QMessageBox.question(self, 'Close window?', 
        #                 'Are you sure?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        # if reply == QtGui.QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()

        # window is closed, emit closed signal and accept the event
        self.closed.emit()
        event.accept()