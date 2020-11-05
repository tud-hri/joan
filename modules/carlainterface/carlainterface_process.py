from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
import sys, glob, os
from core.statesenum import State
#TODO Maybe check this again, however it should not even start when it cant find the library the first time
import time
sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
import carla


class CarlaInterfaceProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events , settings_singleton= settings_singleton)

        # it is possible to read from other modules
        # do_while_running NOT WRITE to other modules' news to prevent spaghetti-code
        self.shared_variables_hardware = news.read_news(JOANModules.HARDWARE_MANAGER)
        self.agent_objects = {}

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings ar converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        #first we make a connection with carla in this multiprocess to get the valid objects we need to spawn our agents
        host = 'localhost'
        port = 2000
        [self.vehicle_blueprint_library, self.spawn_point_objects, self.world, self.spawn_points] = self.connect_carla(host = host, port = port)
        # Now we create our agents and directly spawn them
        for key, value in self._settings_as_object.agents.items():
            self.agent_objects[key] = AgentTypes(value.agent_type).process(self, settings=value, shared_variables=self._module_shared_variables.agents[key])

    def do_while_running(self):
        """
        do_while_running something and write the result in a shared_variable
        """
        for agents in self.agent_objects:
            # will perform the mp input class for eaach available input
            self.agent_objects[agents].do()

        if self._module_shared_variables.state == State.STOPPED.value:
            for agents in self.agent_objects:
                self.agent_objects[agents].destroy()

    def connect_carla(self, host, port):
        "We also want a connection to carla in our multiprocess therefore we need this function here"
        vehicle_tags = []
        spawn_points = []
        client = carla.Client(host, port)  # connecting to server
        client.set_timeout(2.0)
        time.sleep(2)
        world = client.get_world()  # get world object (contains everything)
        blueprint_library = world.get_blueprint_library()
        vehicle_bp_library = blueprint_library.filter('vehicle.*')
        for items in vehicle_bp_library:
            vehicle_tags.append(items.id[8:])
        world_map = world.get_map()
        spawn_point_objects = world_map.get_spawn_points()
        for item in spawn_point_objects:
            spawn_points.append("Spawnpoint " + str(spawn_point_objects.index(item)))

        return vehicle_bp_library, spawn_point_objects, world, spawn_points