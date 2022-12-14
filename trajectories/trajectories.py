

class Track:
    def __init__(self, map_name, current_trajectory=None, other_trajectories_names=None):
        self.map_name = map_name
        self.current_trajectory = current_trajectory
        self.other_trajectories_names = other_trajectories_names
        self.load_track_from_carla()

    def update_current_trajectory(self, trajectory_name):
        self.current_trajectory = trajectory_name

    def load_track_from_carla(self):
        a = None
