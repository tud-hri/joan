from modules.joanmodules import JOANModules


class BaseInput:
    def __init__(self, hardware_manager_action):
        self._carla_interface_data = hardware_manager_action.read_news(JOANModules.AGENT_MANAGER)
        self._action = hardware_manager_action
        self._data = {'SteeringInput': 0, 'ThrottleInput': 0, 'BrakeInput': 0, 'Reverse': False, 'Handbrake': False}
        self.currentInput = 'None'

    def remove_tab(self, tab):
        self._action.remove(tab.groupBox.title())
        tab.setParent(None)

    def process(self):
        return self._data
