"""Action class for JOAN menu"""
# TODO Setting store for modules (which to load, etc, etc): https://doc.qt.io/qt-5/qtcore-serialization-savegame-example.html

from modules.joanmodules import JOANModules
from process import Control


class JOANMenuAction(Control):
    """Action class for JOANMenuWidget"""

    def __init__(self, widget, *args, **kwargs):
        super().__init__()

        # self.moduleStates = None
        # self.moduleStateHandler = None
        # try:
        #     statePackage = self.getModuleStatePackage(module='modules.joanmenu.widget.joanmenu.JOANMenuWidget')
        #     self.moduleStates = statePackage['moduleStates']
        #     self.moduleStateHandler = statePackage['moduleStateHandler']
        # except Exception as e:
        #     print(e)

        self._widget = widget

        self._data = {}
        self.writeNews(channel=self, news=self._data)

        self.path_modules = ''

        # dictionary to keep track of the instantiated modules
        self._instantiated_modules = {}

    def initialize(self):
        """Initialize modules"""
        for _, value in self._instantiated_modules.items():
            value.initialize()

    def start(self):
        """Initialize modules"""
        for _, value in self._instantiated_modules.items():
            value.start()

    def stop(self):
        """Initialize modules"""
        for _, value in self._instantiated_modules.items():
            value.stop()

    def add_module(self, module: JOANModules, name=''):
        """Add module, instantiated module, find unique name"""

        module_widget = module.widget()
        module_widget.setObjectName(name)

        # add instantiated modules to dictionary
        self._instantiated_modules[module] = module_widget

        # update news
        self._data['instantiated_modules'] = self._instantiated_modules
        self.writeNews(channel=self, news=self._data)

        return module_widget

    def remove_module(self, module: JOANModules):
        """ Remove module by name"""

        del self._instantiated_modules[module]

    @property
    def instantiated_modules(self):
        """getter for self._instantiated_modules, only allow get, not set"""
        return self._instantiated_modules
