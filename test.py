import carla
import time
print("trying")
# Connect to the client and retrieve the world object

carla_available = False
while not carla_available:
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)
        world = client.get_world()
        carla_available = True
    except:
        print("Still waiting on carla")

print("carla is available now")


# client.load_world('DebugMap')