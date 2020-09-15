from modules.joanmodules import JOANModules
from modules.hardwaremanager.action.hwinputtypes import HardwareInputTypes
from PyQt5 import uic
from modules.joanmodules import JOANModules

class BaseInput:
    """
    This class is the base class of any (new) input that is implemented. Any implemented input class should inherit from
    this class.
    """

    def __init__(self, hardware_input_type: HardwareInputTypes,  module_action: JOANModules):
        """
        Initializes the class
        :param hardware_manager_action: Uses the action class of the module so we can read the news.
        """
        self.module_action = module_action
        self._hardware_input_type = hardware_input_type

        # widget
        self._settings_tab = uic.loadUi(self._hardware_input_type.settings_ui_file)
        self._hardware_input_tab = uic.loadUi(self._hardware_input_type.hardware_tab_ui_file)

        # widget actions
        self._hardware_input_tab.btn_remove_hardware.clicked.connect(self.remove_hardware_input)

        self._carla_interface_data = self.module_action.read_news(JOANModules.CARLA_INTERFACE)
        self._data = {'steering_angle': 0, 'throttle': 0, 'brake': 0, 'Reverse': False, 'Handbrake': False}
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
        self.module_action.remove_hardware_input_device(self)

    def do(self):
        """
        Processes any input, in this case will just return the current data since there is nothing to core.
        :return: current data
        """
        return self._data
