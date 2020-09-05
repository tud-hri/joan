from modules.joanmodules import JOANModules


class Status:
    """
    The Status class is a singleton that handles all states as defined in the MasterStates class
    To change states the StateHandler class is used
    """
    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = object.__new__(Status)

            cls._module_state_machines = {}  # enum style (e.g. JOANModules.HARDWARE_MANAGER: State.READY)
        return cls.instance

    def update_state_machine(self, module: JOANModules, module_state_machine):
        """
        Set state_machine of every module in the singleton, state_machine holds the current state for his/her own module

        :param module: used as a key
        :param module_state_machine: reference to the module state machine
        :return:
        """
        "  "
        self._module_state_machines.update({module: module_state_machine})

    def get_module_current_state(self, module: JOANModules):
        """
        Return the current state of a module
        :param module: from JOANModules enum
        :return: requested state
        """
        try:
            return self._module_state_machines[module].current_state
        except KeyError:
            return None

    def get_module_state_machine(self, module: JOANModules):
        """
        Return the state machine of the requested module
        :param module:
        :return:
        """
        try:
            return self._module_state_machines[module]
        except KeyError:
            return None
