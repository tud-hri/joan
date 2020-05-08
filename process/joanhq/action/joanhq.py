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

        # status, statehandlers and news
        self.singleton_status = Status()
        self.master_state_handler = self.singleton_status._master_state_handler
        self.master_states = self.singleton_status._master_states
        self.master_state_handler.state_changed.connect(self.handle_master_state)

        self.window = None

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
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.stop()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.stop()

    def add_module(self, module: JOANModules, name='', parent=None, millis=100):
        """Add module, instantiated module, find unique name"""

        if not parent:
            parent = self.window

        if module is JOANModules.FEED_BACK_CONTROLLER or module is JOANModules.TRAJECTORY_RECORDER: 
            # old style
            module_action = None

            module_widget = module.dialog()
            module_widget.setObjectName(name)
            module_dialog = module_widget
        else:
            # TODO Load the default settings for this module here, this can be from a saved settings file or from another source
            # millis = default_millis_for_this_module
            module_action = module.action(self.master_state_handler, millis=millis)
            module_dialog = module.dialog(module_action, self.master_state_handler, parent=parent)

        self.window.add_module(module_dialog, module)

        # add instantiated module to dictionary
        # note: here, we are storing the enums for easy access to both action and widget classes
        self._instantiated_modules[module] = module_action
        
        return module_dialog, module_action

    def remove_module(self, module: JOANModules):
        """ Remove module by name"""

        del self._instantiated_modules[module]

    def handle_master_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.master_state_handler.get_state(state)  # ensure we have the State object (not the int)

            # emergency stop
            if state_as_state == self.master_states.ERROR:
                self.stop()

        except Exception as inst:
            print(inst)

    def emergency(self):
        """Emergency button processing"""
        self.master_state_handler.request_state_change(self.master_states.ERROR)

    def quit(self):
        self.master_state_handler.request_state_change(self.master_states.QUIT)

    @property
    def instantiated_modules(self):
        """getter for self._instantiated_modules, only allow get, not set"""
        return self._instantiated_modules

