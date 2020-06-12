"""Action class for JOAN menu"""
import os
from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.news import News
from process.settings import Settings
from process.statehandler import StateHandler
from process.states import MasterStates
from process.status import Status


class JoanHQAction(QtCore.QObject):
    """Action class for JoanHQ"""

    def __init__(self):
        super(QtCore.QObject, self).__init__()

        self.window = None

        # settings
        self.singleton_settings = Settings()

        # path to modules directory
        self.path_modules = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "modules"))

        # dictionary to keep track of the instantiated modules
        self._instantiated_modules = {}

    def initialize_all(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.initialize()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.initialize()

    def start_all(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.start()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.start()
 
    def stop_all(self):
        """Stop all modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.stop()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.stop()
 
    def add_module(self, module: JOANModules, name='', parent=None, millis=100):
        """Add module, instantiated module, find unique name"""

        if not parent:
            parent = self.window

        '''
        if module is JOANModules.FEED_BACK_CONTROLLER: # or module is JOANModules.TRAJECTORY_RECORDER: 
            # old style
            module_action = None

            module_widget = module.dialog()
            module_widget.setObjectName(name)
            module_dialog = module_widget
        '''
        #else:
        '''
        module_action = module.action(self.master_state_handler, millis=millis)
        module_dialog = module.dialog(module_action, self.master_state_handler, parent=parent)
        '''
        module_action = module.action(millis=millis)
        module_dialog = module.dialog(module_action, parent=parent)

        self.window.add_module(module_dialog, module)

        # add instantiated module to dictionary
        self._instantiated_modules[module] = module_action
        
        return module_dialog, module_action

    def remove_module(self, module: JOANModules):
        """ Remove module by name"""

        del self._instantiated_modules[module]

    def emergency(self):
        """Emergency button processing"""
        self.stop_all()

    def quit(self):
        self.stop_all()

    @property
    def instantiated_modules(self):
        """getter for self._instantiated_modules, only allow get, not set"""
        return self._instantiated_modules

