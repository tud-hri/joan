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
        

        self.fileMenu = self.menuBar().addMenu('File')
        self.fileMenu.addAction('Store settings')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Close')
        self.fileMenu.triggered.connect(self.processFileTrigger)

        self.viewMenu = self.menuBar().addMenu('Show')
        self.viewMenu.triggered.connect(self.processViewTrigger)
        
        # self.askConfirmClose = 'askCloseConfirm' in kwargs.keys() and kwargs['askCloseConfirm'] or False
        # self.showStateWidget = 'showStateWidget' in kwargs.keys() and kwargs['showStateWidget'] or False

    def addWidget(self, widget, name='widget'):
        
        
        # if the default name is given, check if it already exists in the central Widget, and add counter
        if self.mainWidget.findChild(QtWidgets.QWidget, name) is not None:
            for i in range(len(self.mainWidget.findChildren(QtWidgets.QWidget))):
                tmpname = name + '-' + str(i)
                if self.mainWidget.findChild(QtWidgets.QWidget, tmpname) is None:
                    name = tmpname
                    break

        # set widget name
        widget.setObjectName(name)

        # add action for each widget in the view menu: this is used to show the widget
        self.viewMenu.addAction(QtWidgets.QAction(name, self.viewMenu, checkable=True, checked=True))

        # and finally add the widget to the layout of the mainWidget
        self.layout.addWidget(widget)


    def processFileTrigger(self, action):
        '''Using action.text(), you can process the action that is triggered in the file menu, like Save settings or close'''

        if action.text() == 'Close':
            self.close()

    def processViewTrigger(self, action):
        '''Using action.text(), you can process the action that is triggered in the file menu, like Save settings or close'''
        widget = self.mainWidget.findChild(QtWidgets.QWidget, action.text())
        if widget is not None:
            widget.setVisible(action.isChecked())
            self.centralWidget().adjustSize()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()