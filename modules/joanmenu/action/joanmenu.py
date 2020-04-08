"""Action class for JOAN menu"""
# TODO Setting store for modules (which to load, etc, etc): https://doc.qt.io/qt-5/qtcore-serialization-savegame-example.html
import inspect
import sys
import traceback

from PyQt5 import QtCore, QtWidgets

from process import Control
from modules import *

class Instantiate():
    """"
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)

    @param className is the class that will be instantiated
    """

    def __init__(self, className):
        self._class = globals()[className] if className in globals().keys() else None

    def getInstantiatedClass(self):
        """Return instantiated class"""
        try:
            if self._class:
                return self._class()
            else:
                print("Make sure that '%s' is lowercasename and that the class ends with 'Widget'" % self._class)
                return None
        except NameError as inst:
            traceback.print_exc(file=sys.stdout)
            print(inst, self._class)

        return None

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

    def add_module(self, module, name=''):
        """Add module, instantiated module, find unique name"""

        # first, check if a class with the name 'module' is present in the live objects of this module (e.g. whether it is imported).
        # this assumes that the module is imported through the wildcard through: 'from modules import *'
        clsmembers = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))
        found_class = False
        for key, _ in clsmembers.items():
            if key.lower() == module.lower():
                module = key
                found_class = True

        if not found_class:
            print("Module class not found. The module needs to be in its own folder in the 'modules' folder.")
            return None

        # if name is not given, take str(module)
        if name == '':
            name = str(module)

        # check if this name is already taken
        if name in self._instantiated_modules.keys():
            # key exists, prompt user to give a new name

            # first, find new name (appending counter)
            counter = 1
            new_name = '%s-%d' % (name, counter)
            while new_name in self._instantiated_modules.keys():
                new_name = '%s-%d' % (name, counter+1)

            # and create input dialog
            dlg = QtWidgets.QInputDialog(self._widget.window)
            dlg.resize(QtCore.QSize(400, 100))
            dlg.setWindowTitle("Module name already taken, provide new name")
            dlg.setLabelText("New name:")
            dlg.setTextValue(new_name)
            dlg.setTextEchoMode(QtWidgets.QLineEdit.Normal)
            if dlg.exec_() == QtWidgets.QDialog.Accepted:
                name = dlg.textValue()
            # name, _ = QtWidgets.QInputDialog.getText(self._widget, , "New name:", QtWidgets.QLineEdit.Normal, new_name)

        if module in ('JOANMenuWidget'):
            print('You cannot add another JOAN menu')
            return None

        # instantiate class module
        instantiated = Instantiate(module)
        instantiated_class = instantiated.getInstantiatedClass()
        instantiated_class.setObjectName(name)

        # raise typeerror if module/instantiated_class is None
        if instantiated_class is None:
            print("Cannot instantiate class ", module)
            return None

        # add instantiated modules to dictionary
        self._instantiated_modules[name] = instantiated_class

        # update news
        self._data['instantiated_modules'] = self._instantiated_modules
        self.writeNews(channel=self, news=self._data)

        return self._instantiated_modules[name]

    def remove_module(self, name):
        """ Remove module by name"""

        del self._instantiated_modules[name]

    def rename_module(self, old_name, new_name):
        """Rename the module's object name and key in _instantiated_modules dict"""
        self._instantiated_modules[old_name].setObjectName(new_name)
        self._instantiated_modules[new_name] = self._instantiated_modules.pop(old_name)

    @property
    def instantiated_modules(self):
        """getter for self._instantiated_modules, only allow get, not set"""
        return self._instantiated_modules
