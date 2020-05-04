from modules.joanmodules import JOANModules
from .statehandler import StateHandler, MasterStates


class Status:
    """
    The Status class is a singleton that handles all states as defined in the MasterStates class
    To change states the StateHandler class is used
    """
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(Status)
            cls._master_states = MasterStates()
            cls._master_state_handler = StateHandler(first_state=MasterStates.VOID, states_dict=cls._master_states.get_states())
            cls._module_state_packages = {}
        return cls.instance

    def register_module_state_package(self, module: JOANModules, module_state_package):
        self._module_state_packages.update({module: module_state_package})

    def get_module_state_package(self, module: JOANModules):
        try:
            return self._module_state_packages[module]
        except KeyError:
            return {}

    @property
    def all_module_state_packages(self):
        return self._module_state_packages

    @property
    def all_module_state_package_keys(self):
        return self._module_state_packages.keys()
