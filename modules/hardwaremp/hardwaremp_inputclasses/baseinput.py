from modules.joanmodules import JOANModules
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from PyQt5 import uic
from modules.joanmodules import JOANModules

class BaseInput:
    """
    This class acts as an administrative tool to geht the right ui files for any added inputs.
    """

    def __init__(self, hardware_input_type: HardwareInputTypes,  module_manager: JOANModules):
        """
        Initializes the class
        :param hardware_manager_action: Uses the action class of the module so we can read the news.
        """
        self.module_manager = module_manager
        self._hardware_input_type = hardware_input_type

        # widget
        self._settings_tab = uic.loadUi(self._hardware_input_type.settings_ui_file)
        self._hardware_input_tab = uic.loadUi(self._hardware_input_type.hardware_tab_ui_file)

        # widget actions
        self._hardware_input_tab.btn_remove_hardware.clicked.connect(self.remove_hardware_input)

        self.currentInput = 'None'
        self._tab_widget = None

    @property
    def get_hardware_input_tab(self):
        return self._hardware_input_tab

    def initialize(self):
        """initialize, can be overwritten"""
        pass

    def remove_hardware_input(self):
        """Remove the connected tab widget (and tab widget only)"""
        self.module_manager.remove_hardware_input_device(self)

