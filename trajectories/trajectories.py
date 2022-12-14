

class Track:
    def __init__(self, trajectory_name, other_trajectories_names=None):
        self.trajectory_name = trajectory_name
        self.other_trajectories_names = other_trajectories_names
        self.load_track_from_carla()
