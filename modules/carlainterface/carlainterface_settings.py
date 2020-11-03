import enum

from core.module_settings import ModuleSettings, find_settings_by_identifier
from modules.joanmodules import JOANModules
from modules.carlainterface.carlainterface_agenttypes import AgentTypes

class CarlaInterfaceSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.CARLA_INTERFACE)
        self.agents = {}

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """

        module_settings_to_load = loaded_dict[str(self.module)]

        for identifier, settings_dict in module_settings_to_load['agents'].items():
            if 'Ego Vehicle' in identifier:
                ego_vehicle_settings = AgentTypes.EGO_VEHICLE.settings()
                ego_vehicle_settings.set_from_loaded_dict(settings_dict)
                self.agents.update({identifier: ego_vehicle_settings})

    def add_agent(self, agent_type: AgentTypes, agent_settings=None):
        # create empty settings object
        if not agent_settings:
            agent_settings = agent_type.settings()

            nr = 1
            name = '{0!s}_{1}'.format(agent_type, nr)
            while name in self.agents.keys():
                nr += 1
                name = '{0!s}_{1}'.format(agent_type, nr)

            agent_settings.identifier = name

        # add settings to dict, check if settings do not already exist
        if agent_settings not in self.agents.values():
            self.agents[agent_settings.identifier] = agent_settings

        return agent_settings

    def all_agents(self):
        return {**self.agents}

    def remove_agent(self, identifier):
        key, _ = find_settings_by_identifier(self.agents, identifier)
        self.agents.pop(key)

