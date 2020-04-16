"""Base class for modules"""

import os 
from PyQt5 import uic, QtCore

from signals import Pulsar
from .statehandler import StateHandler, MasterStates
from .mainmodulewidget import MainModuleWidget
from .settings import Settings


class News:
    '''
    The News class is a singleton that holds all most recent status data
    Every class has its own writing area; the key of the class
    Oll other classes may read the value
    '''
    instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.instance:
            klass.instance = object.__new__(News)
            klass.news = {}
            # klass.availableKeys = klass.news.keys()

        return klass.instance

    def __init__(self, recentNewsDict, *args, **kwargs):
        self.news.update(recentNewsDict)


class Status:
    '''
    The Status class is a singleton that handles all states as defined in the MasterStates class
    To change states the StateHandler class is used
    '''
    instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.instance:
            klass.instance = object.__new__(Status)
            klass.masterStates = MasterStates()
            klass.masterStateHandler = StateHandler(firstState=MasterStates.VOID, statesDict=klass.masterStates.getStates())
            klass.moduleStatePackages = {}
        return klass.instance

    def __init__(self, moduleStatePackage):
        # TODO find out if self.gui is necessary, also see klass.gui
        # self.gui.update(guiDict)
        self.moduleStatePackages.update(moduleStatePackage)


class Control(Pulsar):
    """Base class for JOAN modules"""

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = 'callback' in kwargs.keys() and kwargs['callback'] or []
        Pulsar.__init__(self, *args, **kwargs)

        # for use in child classes
        self.singletonStatus = Status({})
        self.singletonNews = News({})
        self.masterStateHandler = self.singletonStatus.masterStateHandler
        self.masterStates = self.singletonStatus.masterStates

        self.window = None  # main widget (container for widget and controlWidget)
        self.widget = None  # will contain a value after calling createWidget
        self.stateWidget = None
        self.moduleStateHandler = None  # will contain  a value after calling defineModuleStateHandler
        self.moduleStates = None  # will contain  a value after calling defineModuleStateHandler
        self.initialized = False

    def initialize(self):
        """Method to initialize the module before start"""
        # self.initialized = True

    def createWidget(self, ui=''):
        assert ui != '', 'argument "ui" should point to a PyQt ui file (e.g. ui=<absolute path>menu.ui)'

        # window is a QMainWindow, and the container for all widgets
        self.window = MainModuleWidget()

        self.settings = Settings(file=os.path.join(os.path.dirname(ui), 'modulesettings.json'))

        self.stateWidget = self._getGui(os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "../resources/statewidget.ui"))
        self.window.addWidget(self.stateWidget, name='State widget')

        # load widget UI ()
        self.widget = self._getGui(ui)
        assert self.widget is not None, 'could not create a widget, is %s the correct filename?' % ui
        self.window.addWidget(self.widget, name='Module widget')

        # connect self.window close signal to the widget's _close function (if defined): this will also call self._close in case the user closes the window
        try:
            self.window.closed.connect(self._close)
        except NotImplementedError:
            pass

        # connect stateWidget widgets (buttons, line edit)
        self.stateWidget.inputTickMillis.setPlaceholderText(str(self.millis))
        self.stateWidget.inputTickMillis.textChanged.connect(lambda dt=self.millis: self._setmillis(dt))
        self.stateWidget.btnStart.clicked.connect(self._btnStartClicked)
        self.stateWidget.btnStop.clicked.connect(self._btnStopClicked)

        try:
            self.stateWidget.lbModuleState.setText(self.moduleStateHandler.getCurrentState().name)
            self.moduleStateHandler.stateChanged.connect(
                lambda state: self.stateWidget.lbModuleState.setText(self.moduleStateHandler.getState(state).name)
            )
        except Exception as e:
            print("TODO: we should create the moduleStateHandler first thing per module in __init__ before calling createWidget")

    def _btnStartClicked(self):
        self.start()
        self.stateWidget.inputTickMillis.setEnabled(False)
        self.stateWidget.inputTickMillis.clear()
        self.stateWidget.inputTickMillis.clearFocus()
        self.stateWidget.inputTickMillis.setPlaceholderText(str(self.millis))

    def _btnStopClicked(self):
        self.stop()
        self.stateWidget.inputTickMillis.setEnabled(True)
        self.stateWidget.inputTickMillis.clear()
        self.stateWidget.inputTickMillis.setPlaceholderText(str(self.millis))

    def _getGui(self, ui=''):
        try:
            return uic.loadUi(ui)
        except OSError as inst:
            print(inst)
            return None

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            assert millis > 0, 'QTimer tick interval needs to be larger than 0'
            self.setInterval(millis)
        except ValueError as e:
            print(e)

    def _show(self):
        self.window.show()

    def _close(self):
        self.window.close()

    def defineModuleStateHandler(self, module='', moduleStates=None):
        assert module != '', 'argument "module" should containt the name of the module, which is the calling class'
        # states example:     VOID = State(0, translate('BootStates', 'Null state'), -1,150)
        moduleStatesDict = moduleStates.getStates()
        self.moduleStateHandler = StateHandler(firstState=MasterStates.VOID, statesDict=moduleStatesDict)
        self.moduleStates = moduleStates
    
        try:
            moduleKey = '%s.%s' % (module.__class__.__module__, module.__class__.__name__)
            moduleStatePackage = {}
            moduleStatePackage['moduleStates'] = moduleStates
            moduleStatePackage['moduleStateHandler'] = self.moduleStateHandler
            self.singletonStatus = Status({moduleKey: moduleStatePackage})
        except Exception as e:
            print('Exception in Control', e)

    def writeNews(self, channel='', news={}):
        """write new data to channel"""

        assert channel != '', 'argument "channel" should be the writer class'
        assert type(news) == dict, 'argument "news" should be of type dict and will contain news(=data) of this channel'
        try:
            channelKey = '%s.%s' % (channel.__class__.__module__, channel.__class__.__name__)
            # if channelKey not in self.getAvailableNewsChannels():
            self.singletonNews = News({channelKey: news})
        except Exception as e:
            print(e)

    def getAllNews(self):
        return self.singletonNews.news

    def getAvailableNewsChannels(self):
        return self.singletonNews.news.keys()

    def readNews(self, channel=''):
        return channel in self.getAvailableNewsChannels() and self.singletonNews.news[channel] or {}

    def getAllModuleStatePackages(self):
        return self.singletonStatus.moduleStatePackages

    def getAvailableModuleStatePackages(self):
        return self.singletonStatus.moduleStatePackages.keys()

    def getModuleStatePackage(self, module=''):
        return module in self.getAvailableModuleStatePackages() and self.singletonStatus.moduleStatePackages[module] or {}
