"""Base class for modules"""

import os
from PyQt5 import uic, QtCore, QtGui

from signals import Pulsar
from .statehandler import StateHandler, MasterStates
from .mainmodulewidget import MainModuleWidget
from .settings import ModuleSettings


class Settings:
    '''
    The Settings class is a singleton that holds settings of module, 
    so they can be used from Experiment classes, using the module_key
    '''
    instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.instance:
            klass.instance = object.__new__(Settings)
            klass.settings = {}
        return klass.instance

    def __init__(self, settings_dict):
        self.settings.update(settings_dict)

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
            klass.master_states = MasterStates()
            klass.master_state_handler = StateHandler(first_state=MasterStates.VOID, states_dict=klass.master_states.get_states())
            klass.module_state_packages = {}
        return klass.instance

    def __init__(self, module_state_package):
        # TODO find out if self.gui is necessary, also see klass.gui
        # self.gui.update(guiDict)
        self.module_state_packages.update(module_state_package)


class Control(Pulsar):
    """Base class for JOAN modules"""

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = 'callback' in kwargs.keys() and kwargs['callback'] or []
        Pulsar.__init__(self, *args, **kwargs)

        # for use in child classes
        self.singleton_status = Status({})
        self.singleton_news = News({})
        self.singleton_settings = Settings({})
        self.master_state_handler = self.singleton_status.master_state_handler
        self.master_states = self.singleton_status.master_states
        #self.Settings(file=os.path.join(os.path.dirname(ui), 'modulesettings.json'))


        self.window = None  # main widget (container for widget and controlWidget)
        self.widget = None  # will contain a value after calling create_widget
        self.state_widget = None
        self.module_state_handler = None  # will contain  a value after calling define_module_state_handler
        self.module_states = None  # will contain  a value after calling define_module_state_handler
        self.initialized = False

    def initialize(self):
        """Method to initialize the module before start"""
        # self.initialized = True

    def create_widget(self, ui=''):
        assert ui != '', 'argument "ui" should point to a PyQt ui file (e.g. ui=<absolute path>menu.ui)'

        # window is a QMainWindow, and the container for all widgets
        self.window = MainModuleWidget()

        #self.settings = Settings(file=os.path.join(os.path.dirname(ui), 'modulesettings.json'))

        self.state_widget = self._get_gui(os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "../resources/statewidget.ui"))
        self.window.addWidget(self.state_widget, name='State widget')

        # load widget UI ()
        self.widget = uic.loadUi(ui)
        assert self.widget is not None, 'could not create a widget, is %s the correct filename?' % ui
        self.window.addWidget(self.widget, name='Module widget')

        # connect self.window close signal to the widget's _close function (if defined): this will also call self._close in case the user closes the window
        try:
            self.window.closed.connect(self._close)
        except NotImplementedError:
            pass

        # connect stateWidget widgets (buttons, line edit)
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.millis))
        self.state_widget.input_tick_millis.textChanged.connect(lambda dt=1: self._setmillis(dt))
        # self.state_widget.input_tick_millis.setValidator(QtGui.QIntValidator(0, 2000, self))  # only allow 0-2000ms and int
        self.state_widget.btn_start.clicked.connect(self._btn_start_clicked)
        self.state_widget.btn_stop.clicked.connect(self._btn_stop_clicked)

        try:
            self.state_widget.lb_module_state.setText(self.module_state_handler.get_current_state().name)
            self.module_state_handler.state_changed.connect(
                lambda state: self.state_widget.lb_module_state.setText(self.module_state_handler.get_state(state).name)
            )
        except Exception as e:
            print("TODO: we should create the module_state_handler first thing per module in __init__ before calling create_widget")

    def _btn_start_clicked(self):
        self.start()
        self.state_widget.input_tick_millis.setEnabled(False)
        self.state_widget.input_tick_millis.clear()
        self.state_widget.input_tick_millis.clearFocus()
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.millis))

    def _btn_stop_clicked(self):
        self.stop()
        self.state_widget.input_tick_millis.setEnabled(True)
        self.state_widget.input_tick_millis.clear()
        self.state_widget.input_tick_millis.setPlaceholderText(str(self.millis))

    def _get_gui(self, ui=''):
        try:
            return uic.loadUi(ui)
        except OSError as inst:
            print(inst)
            return None

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        print(millis)
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

    def define_module_state_handler(self, module='', module_states=None):
        assert module != '', 'argument "module" should containt the name of the module, which is the calling class'
        # states example:     VOID = State(0, translate('BootStates', 'Null state'), -1,150)
        module_states_dict = module_states.get_states()
        self.module_state_handler = StateHandler(first_state=MasterStates.VOID, states_dict=module_states_dict)
        self.module_states = module_states

        try:
            module_key = '%s.%s' % (module.__class__.__module__, module.__class__.__name__)
            module_state_package = {}
            module_state_package['module_states'] = module_states
            module_state_package['module_state_handler'] = self.module_state_handler
            self.singleton_status = Status({module_key: module_state_package})
        except Exception as e:
            print('Exception in Control', e)

    def write_news(self, channel='', news={}):
        """write new data to channel"""

        assert channel != '', 'argument "channel" should be the writer class'
        assert type(news) == dict, 'argument "news" should be of type dict and will contain news(=data) of this channel'
        try:
            channel_key = '%s.%s' % (channel.__class__.__module__, channel.__class__.__name__)
            # if channel_key not in self.get_available_news_channels():
            self.singleton_news = News({channel_key: news})
        except Exception as e:
            print(e)

    def create_settings(self, module='', file=''):
        """ 
        When called, other childs of Control can use these settings from modules
        File should be placed within the calling module directory. 
        When removing a module the corresponding settings are also removed, which is a good thing.
        """
        assert module != '', 'argument "module" should containt the name of the module, which is the calling class'
        assert file != '', 'argument "file" should contain the full path with a filename that ends with ".json"'
        assert file.endswith('.json'), 'argument "file" should contain the full path with a filename that ends with ".json"'
        try:
            module_key = '%s.%s' % (module.__class__.__module__, module.__class__.__name__)
            settings = ModuleSettings(file=file)
            self.singleton_settings = Settings({module_key: settings})
        except Exception as e:
            print('Exception in Control', e)

    def get_all_news(self):
        return self.singleton_news.news

    def get_available_news_channels(self):
        return self.singleton_news.news.keys()

    def read_news(self, channel=''):
        return channel in self.get_available_news_channels() and self.singleton_news.news[channel] or {}

    def get_all_module_state_packages(self):
        return self.singleton_status.module_state_packages

    def get_available_module_state_packages(self):
        return self.singleton_status.module_state_packages.keys()

    def get_module_state_package(self, module=''):
        return module in self.get_available_module_state_packages() and self.singleton_status.module_state_packages[module] or {}

    def get_available_module_settings(self):
        return self.singleton_settings.settings.keys()

    def get_module_settings(self, module=''):
        return module in self.get_available_module_settings() and self.singleton_settings.settings[module] or None
        
