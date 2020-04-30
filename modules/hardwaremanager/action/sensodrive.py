from modules.hardwaremanager.action.baseinput import BaseInput


class JOAN_SensoDrive(BaseInput):  # DEPRECATED FOR NOW
    def __init__(self, hardware_manager_action, sensodrive_tab):
        super().__init__(hardware_manager_action)
        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        self.remove_tab(self._sensodrive_tab)
