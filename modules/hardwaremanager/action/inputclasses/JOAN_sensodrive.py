from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput


class JOAN_SensoDrive(BaseInput):  # DEPRECATED FOR NOW TODO: remove from interface for now
    def __init__(self, hardware_manager_action, sensodrive_tab):
        super().__init__(hardware_manager_action)
        raise NotImplementedError('Mouse input is not yet implemented')
        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        self.remove_tab(self._sensodrive_tab)
