from modules.joanmodules import JOANModules
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput


class JOAN_Mouse(BaseInput):  # DEPRECATED FOR NOW
    def __init__(self, hardware_manager_action, mouse_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'Mouse'
        # Add the tab to the widget
        self._mouse_tab = mouse_tab
        self._mouse_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        self.remove_tab(self._mouse_tab)

    def process(self):
        if (self._carla_interface_data['vehicles'] is not None):
            # self._carla_interface_data = self._action.read_news(JoanModules.CARLA_INTERFACE)

            # for vehicles in self._carla_interface_data['vehicles']:
            #     if vehicles.selected_input == self._mouse_tab.groupBox.title():
            #         self._mouse_tab.btn_remove_hardware.setEnabled(False)
            #         break
            #     else:
            #         self._mouse_tab.btn_remove_hardware.setEnabled(True)

            return self._data
