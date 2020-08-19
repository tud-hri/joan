from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput


class JOANMouse(BaseInput):  # DEPRECATED FOR NOW  TODO: remove from interface for now
    """
       Main class for the Mouseinput, inherits from BaseInput (as it should!)
       NOTE: This class is currently not used!!
    """

    def __init__(self, hardware_manager_action, mouse_tab):
        """
        Initializes the class
        :param hardware_manager_action:
        :param mouse_tab:
        """
        super().__init__(hardware_manager_action)
        raise NotImplementedError('Mouse input is not yet implemented')
        self.currentInput = 'Mouse'
        # Add the tab to the widget
        self._mouse_tab = mouse_tab
        self._mouse_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        """
        Removes the mouse from the widget and settings
        NOTE: calls 'self.remove_tab' which is a function of the BaseInput class, if you do not do this the tab will not
        actually disappear from the module.
        :return:
        """
        self.remove_tab(self._mouse_tab)

    def process(self):
        return self._data
