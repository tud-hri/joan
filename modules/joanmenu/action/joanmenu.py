"""Action class for JOAN menu"""
import os
import sys
from PyQt5 import QtWidgets

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

        self.masterStateHandler.stateChanged.connect(self.handle_master_state)

        self._widget = widget

        self._data = {}
        self.writeNews(channel=self, news=self._data)

        # path to modules directory
        self.path_modules = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../", "modules"))

        # dictionary to keep track of the instantiated modules
        self._instantiated_modules = {}

    def initialize(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.initialize()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.initialize()

    def start(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.start()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.start()

    def stop(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            try:
                module.action.stop()
            except AttributeError:  # module has new style TODO: remove statement above when moving to new style
                module.stop()

    def add_module(self, module: JOANModules, name='', parent=None):
        """Add module, instantiated module, find unique name"""

        if module is JOANModules.TEMPLATE:  # Example of how the new style could be
            # TODO Load the default settings for this module here, this can be from a saved settings file or from another source
            # millis = default_millis_for_this_module
            # callbacks = default_callbacks_for_this_module

            module_action = module.action(self.masterStateHandler, millis=100, callbacks=[])
            module_dialog = module.dialog(module_action, self.masterStateHandler, parent=parent)

            module_widget = module_dialog  # to keep the names equal, should be removed when the if template statement is removed
        else: # module has old style TODO: remove statements below when moving to new style
            module_action = None

            module_widget = module.dialog()
            module_widget.setObjectName(name)

        # add instantiated module to dictionary
        # note: here, we are storing the enums for easy access to both action and widget classes
        self._instantiated_modules[module] = module_action if module_action else module_widget  # TODO remove if else statement when moving to new style

        # update news
        self._data['instantiated_modules'] = self._instantiated_modules
        self.writeNews(channel=self, news=self._data)
        
        return module_widget, module_action

    def remove_module(self, module: JOANModules):
        """ Remove module by name"""

        del self._instantiated_modules[module]

    def handle_master_state(self, state):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            state_as_state = self.masterStateHandler.getState(state)  # ensure we have the State object (not the int)

            # self._main_widget.lblMasterState.setText(state_as_state.name)

            # emergency stop
            if state_as_state == self.masterStates.ERROR:
                self.stop()

        except Exception as inst:
            print(inst)

    def emergency(self):
        """Emergency button processing"""
        self.masterStateHandler.requestStateChange(self.masterStates.ERROR)

    def quit(self):
        """Quit button processing"""
        reply = QtWidgets.QMessageBox.question(
            self.window, 'Quit JOAN', 'Are you sure?',
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.app_is_quiting.emit()
            sys.exit()

    @property
    def instantiated_modules(self):
        """getter for self._instantiated_modules, only allow get, not set"""
        return self._instantiated_modules
