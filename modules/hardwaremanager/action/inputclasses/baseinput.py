from modules.joanmodules import JOANModules


class BaseInput:
    """
    This class is the base class of any (new) input that is implemented. Any implemented input class should inherit from
    this class.
    """
    def __init__(self, hardware_manager_action):
        """
        Initializes the class
        :param hardware_manager_action: Uses the action class of the module so we can read the news.
        """
        self._carla_interface_data = hardware_manager_action.read_news(JOANModules.AGENT_MANAGER)
        self._action = hardware_manager_action
        self._data = {'SteeringInput': 0, 'ThrottleInput': 0, 'BrakeInput': 0, 'Reverse': False, 'Handbrake': False}
        self.currentInput = 'None'

    def remove_tab(self, tab):
        """
        This function removes the widget from the module. NOTE: this function can be overwritten in new inputclasses but
        this is not recommended.
        :param tab: the Widget
        :return: -
        """
        self._action.remove(tab.groupBox.title())
        tab.setParent(None)

    def process(self):
        """
        Processes any input, in this case will just return the current data since there is nothing to process.
        :return: current data
        """
        return self._data
