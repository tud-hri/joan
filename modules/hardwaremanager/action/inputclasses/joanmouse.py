from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput


class JOANMouse(BaseInput):  # DEPRECATED FOR NOW  TODO: remove_input_device from interface for now
    """
       Main class for the Mouseinput, inherits from BaseInput (as it should!)
       NOTE: This class is currently not used!!
    """

    def __init__(self, hardware_manager_action):
        """
        Initializes the class
        :param hardware_manager_action:
        :param mouse_tab:
        """
        super().__init__(hardware_manager_action)
        raise NotImplementedError('Mouse input is not yet implemented')
        self.currentInput = 'Mouse'
        # Add the tab to the widget

    def connect_widget(self, widget):
        self._tab_widget = widget
        self._tab_widget.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        """
        Removes the mouse from the widget and settings
        NOTE: calls 'self.remove_tab' which is a function of the BaseInput class, if you do not do this the tab will not
        actually disappear from the module.
        :return:
        """
        self.remove_tab(self._tab_widget)

    def process(self):
        return self._data
