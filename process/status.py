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

            cls._module_state_machines = {}  # enum style (e.g. JOANModules.HARDWARE_MANAGER: State.READY)
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
    

    def update_state_machine(self, module: JOANModules, module_state_machine):
        " set state_machine of every module in the singleton, state_machine holds the current state for his/her own module "
        self._module_state_machines.update({module: module_state_machine})

    def get_module_current_state(self, module: JOANModules):
        try:
            return self._module_state_machines[module].current_state
        except KeyError:
            return None

    def get_module_state_machine(self, module: JOANModules):
        """ Return the state machine of the requested module"""
        try:
            return self._module_state_machines[module]
        except KeyError:
            return None

    # will become deprecated after enum
    @property
    def all_module_state_packages(self):
        return self._module_state_packages

    # will become deprecated after enum
    @property
    def all_module_state_package_keys(self):
        return self._module_state_packages.keys()
