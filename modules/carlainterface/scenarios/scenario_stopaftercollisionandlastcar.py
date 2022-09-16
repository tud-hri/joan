from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
import math
import time

class ScenarioStopAfterNPCVehicleFive:
    def __init__(self):
        self.close_to_followed_car = False
        self.time = None

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        # find location for stop trigger, in our case this is a waypoint in the CARLA map
        ego_agent_key = 'Ego Vehicle_1'
        threshold_time = 7.5  # seconds
        threshold_distance = 10.  # meters

        # Find last agent
        ego_vehicle = carla_interface_process.agent_objects[ego_agent_key]
        if ego_vehicle.spawned_vehicle is not None:
            labels = []
            distances = {}

            for key, value in carla_interface_process.agent_objects.items():
                if 'NPC' in key:
                    distances[key] = self._compute_distance(carla_interface_process, key, ego_agent_key)
                    labels.append(key)
            labels.sort()
            if not labels:
                followed_car_key = ego_agent_key
                print("You cannot use this scenario without NPC vehicles!!")
            else:
                followed_car_key = labels[-1]

            # Getting positions
            if distances[followed_car_key] < threshold_distance:
                self.close_to_followed_car = True
                self.time = time.time()

            if self.close_to_followed_car:
                if (time.time() - self.time) > threshold_time:
                    # request stop
                    self.close_to_followed_car = False
                    self.time = None
                    carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            else:
                self.time = time.time()

    @staticmethod
    def _compute_distance(carla_interface_process, key, ego_agent_key):
        p_ego = carla_interface_process.agent_objects[ego_agent_key].shared_variables.transform
        p_npc = carla_interface_process.agent_objects[key].shared_variables.transform

        # calculate distance between ego_vehicle and spawn point
        distance = math.sqrt((p_ego[0] - p_npc[0]) ** 2 + (p_ego[1] - p_npc[1]) ** 2)
        return distance

    @property
    def name(self):
        return "Stop trial after NPC Vehicles or collision"
