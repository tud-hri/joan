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
            module.action().initialize()

    def start(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            module.action().start()

    def stop(self):
        """Initialize modules"""
        for _, module in self._instantiated_modules.items():
            module.action().stop()

    def add_module(self, module: JOANModules, name=''):
        """Add module, instantiated module, find unique name"""

        module_widget = module.widget()
        module_widget.setObjectName(name)

        # add instantiated module to dictionary
        # note: here, we are storing the enums for easy access to both action and widget classes
        self._instantiated_modules[module] = module

        # update news
        self._data['instantiated_modules'] = self._instantiated_modules
        self.writeNews(channel=self, news=self._data)
        
        return module_widget

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
