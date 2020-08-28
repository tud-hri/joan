from modules.joanmodules import JOANModules


class BaseInput:
    """
    This class is the base class of any (new) input that is implemented. Any implemented input class should inherit from
    this class.
    """

    def __init__(self, hardware_manager_action, name=''):
        """
        Initializes the class
        :param hardware_manager_action: Uses the action class of the module so we can read the news.
        """
        self.name = name
        self.module_action = hardware_manager_action
        self._carla_interface_data = self.module_action.read_news(JOANModules.CARLA_INTERFACE)
        self._data = {'SteeringInput': 0, 'ThrottleInput': 0, 'BrakeInput': 0, 'Reverse': False, 'Handbrake': False}
        self.currentInput = 'None'
        self._tab_widget = None

    def initialize(self):
        """initialize, can be overwritten"""
        pass

    def remove_tab(self):
        """Remove the connected tab widget (and tab widget only)"""
        if self._tab_widget is not None:
            self._tab_widget.setParent(None)

    def do(self):
        """
        Processes any input, in this case will just return the current data since there is nothing to process.
        :return: current data
        """
        return self._data
