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
            # start deprecated 
            cls._master_states = MasterStates()
            cls._master_state_handler = StateHandler(first_state=MasterStates.VOID, states_dict=cls._master_states.get_states())
            cls._module_state_packages = {}
            # end deprecated

            cls._current_state = {}  # enum style (e.g. JOANModules.HARDWARE_MANAGER: State.READY)
        return cls.instance

    # will become deprecated after enum
    def register_module_state_package(self, module: JOANModules, module_state_package):
        self._module_state_packages.update({module: module_state_package})

    # will become deprecated after enum
    def get_module_state_package(self, module: JOANModules):
        try:
            return self._module_state_packages[module]
        except KeyError:
            return {}

    def update_state(self, module: JOANModules, module_state_machine):
        " set state_machine of every module in the singleton, state_machine holds the current state for his/her own module "
        self._current_state.update({module: module_state_machine})

    def get_module_current_state(self, module: JOANModules):
        try:
            return self._current_state[module].current_state
        except KeyError:
            return {}
 
    @property
    def all_module_state_packages(self):
        return self._module_state_packages

    @property
    def all_module_state_package_keys(self):
        return self._module_state_packages.keys()
