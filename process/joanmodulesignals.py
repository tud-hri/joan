
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from modules.joanmodules import JOANModules


class JoanModuleSignal(QtCore.QObject):

    # pyqtSignals need to be class attributes...
    start_module = pyqtSignal()
    stop_module = pyqtSignal()
    initialize_module = pyqtSignal()

    def __init__(self, module_enum: JOANModules):
        """
        Initialize
        :param module_enum: module type
        """
        super(QtCore.QObject, self).__init__()

        self._module_enum = module_enum

