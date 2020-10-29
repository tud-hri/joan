from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from core.hq.hq_manager import HQManager

class CarlaInterfaceManager(ModuleManager):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.CARLA_INTERFACE, time_step_in_ms=time_step_in_ms, parent=parent)
        self._agent_settingdialogs_dict = {}

    def _open_settings_dialog(self, input_name):
        self._agent_settingdialogs_dict[input_name].show()

    def _add_agent(self, agent_type, agent_settings=None):
        """
        Add hardware agent
        :param agent_type:
        :param agent_settings:
        :return:
        """
        if not agent_settings:
            agent_settings = agent_type.settings(agent_type)

            # find unique identifier
            type_dict = None
            if agent_type == AgentTypes.EGO_VEHICLE:
                type_dict = self.module_settings.ego_vehicles

            identifier = 0
            for v in type_dict.values():
                if v.identifier > identifier:
                    identifier = v.identifier
            agent_settings.identifier = identifier + 1

        # check if settings do not already exist
        if agent_type == AgentTypes.EGO_VEHICLE:
            if agent_settings not in self.module_settings.ego_vehicles.values():
                self.module_settings.ego_vehicles[agent_settings.identifier] = agent_settings

        # create dialog thing
        agent_name = '{0!s} {1!s}'.format(agent_type, str(agent_settings.identifier))
        self._agent_settingdialogs_dict[agent_name] = agent_type.klass_dialog(agent_settings)
        return agent_name

    def _remove_agent(self, agent_name):
        # Remove settings if they are available
        settings_object = None

        if 'Ego Vehicle' in agent_name:
            identifier = int(agent_name.replace('Ego Vehicle', ''))
            for egovehicle in self.module_settings.ego_vehicles.values():
                if egovehicle.identifier == identifier:
                    settings_object = egovehicle

        self.module_settings.remove_agent(settings_object)

        # Remove settings dialog
        self._agent_settingdialogs_dict[agent_name].setParent(None)
        del self._agent_settingdialogs_dict[agent_name]

    def _get_update_from_other_modules(self):
        print(self.module.dialog.parent())
