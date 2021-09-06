import glob
import os
import sys

from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
from modules.joanmodules import JOANModules

try:
    sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    import carla
except IndexError as inst:
    print("ScenarioStopTrialAtLocation: CarlaAPI could not be loaded:", inst)


class ScenarioStopTrialAtLocation:

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        # check whether ego_vehicle (specifically 'Ego Vehicle_1') is near its initial waypoint
        stop_trial = False
        trial_time = carla_interface_process.running_time_seconds()
        threshold_time = 60.  # seconds
        threshold_location = 1.  # meters
        ego_agent_key = 'Ego Vehicle 1'

        ego_vehicle = carla_interface_process.agent_objects[ego_agent_key]
        if ego_vehicle.spawned_vehicle is not None:
            p_ego = carla_interface_process.agent_objects[ego_agent_key].transform
            sp = carla_interface_process.spawn_point_objects[
                carla_interface_process.spawn_points.index(carla_interface_process._settings_as_object.agents[ego_agent_key].selected_spawnpoint)]
            # calculate distance between ego_vehicle and spawn point
            distance = sp.location.distance(carla.Location(x=p_ego[0], y=p_ego[1], z=p_ego[2]))

            if (distance < threshold_location) and (trial_time > threshold_time):
                # request stop
                carla_interface_process.pipe_comm.send({"stop_all_modules": True})

    @property
    def name(self):
        return "Stop trial at start location"
