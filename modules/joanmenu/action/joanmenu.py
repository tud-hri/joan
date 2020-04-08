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

        self.pathModules = ''

        # dictionary to keep track of the instantiated modules
        self._instantiatedModules = {}

    def initialize(self):
        """Initialize modules"""
        for _, value in self._instantiatedModules.items():
            value.initialize()

    def start(self):
        """Initialize modules"""
        for _, value in self._instantiatedModules.items():
            value.start()

    def stop(self):
        """Initialize modules"""
        for _, value in self._instantiatedModules.items():
            value.stop()

    def add_module(self, module, name=''):
        """Add module, instantiated module, find unique name"""

        # first, check if a class with the name 'module' is present in the live objects of this module (e.g. whether it is imported).
        # this assumes that the module is imported through the wildcard through: 'from modules import *'
        clsmembers = dict(inspect.getmembers(sys.modules[__name__], inspect.isclass))
        foundClass = False
        for key, _ in clsmembers.items():
            if key.lower() == module.lower():
                module = key
                foundClass = True

        if foundClass is False:
            print("Module class not found. The module needs to be in its own folder in the 'modules' folder.")
            return None

        # if name is not given, take str(module)
        if name == '':
            name = str(module)

        # check if this name is already taken
        if name in self._instantiatedModules.keys():
            # key exists, prompt user to give a new name

            # first, find new name (appending counter)
            counter = 1
            newName = '%s-%d' % (name, counter)
            while newName in self._instantiatedModules.keys():
                newName = '%s-%d' % (name, counter+1)

            # and create input dialog
            dlg = QtWidgets.QInputDialog(self._widget.window)
            dlg.resize(QtCore.QSize(400, 100))
            dlg.setWindowTitle("Module name already taken, provide new name")
            dlg.setLabelText("New name:")
            dlg.setTextValue(newName)
            dlg.setTextEchoMode(QtWidgets.QLineEdit.Normal)
            if dlg.exec_() == QtWidgets.QDialog.Accepted:
                name = dlg.textValue()
            # name, _ = QtWidgets.QInputDialog.getText(self._widget, , "New name:", QtWidgets.QLineEdit.Normal, newName)

        if module in ('JOANMenuWidget'):
            print('You cannot add another JOAN menu')
            return None

        # instantiate class module
        instantiated = Instantiate(module)
        instantiatedClass = instantiated.getInstantiatedClass()
        instantiatedClass.setObjectName(name)

        # raise typeerror if module/instantiatedClass is None
        if instantiatedClass is None:
            print("Cannot instantiate class ", module)
            return None

        # add instantiated modules to dictionary
        self._instantiatedModules[name] = instantiatedClass

        # update news
        self._data['instantiatedModules'] = self._instantiatedModules
        self.writeNews(channel=self, news=self._data)

        return self._instantiatedModules[name]

    def removeModule(self, name):
        """ Remove module by name"""

        del self._instantiatedModules[name]

    def renameModule(self, oldName, newName):
        """Rename the module's object name and key in _instantiatedModules dict"""
        self._instantiatedModules[oldName].setObjectName(newName)
        self._instantiatedModules[newName] = self._instantiatedModules.pop(oldName)

    @property
    def instantiatedModules(self):
        """getter for self._instantiatedModules, only allow get, not set"""
        return self._instantiatedModules
