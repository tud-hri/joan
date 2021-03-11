from core.module_settings import ModuleSettings, find_settings_by_identifier
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from modules.joanmodules import JOANModules


class CarlaInterfaceSettings(ModuleSettings):
    """
    CarlaInterfaceSettings module, inherits from the ModuleSettings
    """
    def __init__(self):
        """
        Initialize
        """
        super().__init__(JOANModules.CARLA_INTERFACE)
        self.agents = {}

    def reset(self):
        self.agents = {}

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        self.reset()
        module_settings_to_load = loaded_dict[str(self.module)]

        for identifier, settings_dict in module_settings_to_load['agents'].items():
            if str(AgentTypes.EGO_VEHICLE) in identifier:
                ego_vehicle_settings = AgentTypes.EGO_VEHICLE.settings()
                ego_vehicle_settings.set_from_loaded_dict(settings_dict)
                self.agents.update({identifier: ego_vehicle_settings})
            elif str(AgentTypes.NPC_VEHICLE) in identifier:
                npc_vehicle_settings = AgentTypes.NPC_VEHICLE.settings()
                npc_vehicle_settings.set_from_loaded_dict(settings_dict)
                self.agents.update({identifier: npc_vehicle_settings})

    def add_agent(self, agent_type: AgentTypes, agent_settings=None):
        """
        Add agents to class attribute
        :param agent_type: agent type, see enum AgentTypes
        :param agent_settings: settings for this agent
        :return: renewed agent settings
        """
        # create empty settings object
        if not agent_settings:
            agent_settings = agent_type.settings()

            number = 1
            name = '{0!s}_{1}'.format(agent_type, number)
            while name in self.agents.keys():
                number += 1
                name = '{0!s}_{1}'.format(agent_type, number)

            agent_settings.identifier = name

        # add settings to dict, check if settings do not already exist
        if agent_settings not in self.agents.values():
            self.agents[agent_settings.identifier] = agent_settings

        return agent_settings

    def all_agents(self):
        """
        :return: all agents
        """
        return {**self.agents}

    def remove_agent(self, identifier):
        """
        Removes an agent
        :param identifier: identifies an agent
        """
        key, _ = find_settings_by_identifier(self.agents, identifier)
        self.agents.pop(key)
