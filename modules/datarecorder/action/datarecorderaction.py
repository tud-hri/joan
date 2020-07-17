import os
from pathlib import Path
from datetime import datetime
import math
import numpy as np

from modules.datarecorder.action.datawriter import DataWriter
from modules.datarecorder.action.datarecordersettings import DataRecorderSettings
from modules.joanmodules import JOANModules

from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State
from process.status import Status

class DatarecorderAction(JoanModuleAction):
    """
    Does all kinds of action concerning the Datarecorder module
    Inherits actions from the JoanModuleActions
    """
    def __init__(self, millis=200):
        """
        :param millis: contains the value of the writing interval
        """
        super().__init__(module=JOANModules.DATA_RECORDER, millis=millis)
        
        self.status = Status()

        # next three Template lines are not used for datarecorder' 
        # 1. self.data['t'] = 0
        # 2. self.write_news(news=self.data)
        # 3. self.time = QtCore.QTime()
    
        # trajectory recorder:
        self.trajectory_recorder = Trajectory_recorder(self, 0.1)

        # start settings for this module
        self.settings = DataRecorderSettings(JOANModules.DATA_RECORDER)
        self.default_settings_file_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'datarecordersettings.json')

        if Path(self.default_settings_file_location).is_file():
            self.load_settings_from_file(self.default_settings_file_location)
            self.millis = self.settings.write_interval
        else:
            self.settings.set_all_true()
            self.settings.write_interval = 100
            self.save_settings_to_file(self.default_settings_file_location)

        self.share_settings(self.settings)
        # end settings for this module

        self.filename = ''
        self.data_writer = DataWriter(news=self.get_all_news(), 
                                      channels=self.get_available_news_channels(),
                                      settings=self.get_module_settings(JOANModules.DATA_RECORDER))
        # TODO: run data_writer in separate thread
        #self.data_writer.start()

    def initialize_file(self):
        """
        Createsd a filename with extension 
        """
        self.filename = self._create_filename(extension='csv')

    def load_settings_from_file(self, settings_file_to_load):
        """
        Loads the settings file for the Datarecorder and saves these settings in the default settings file location
        Sets the write interval from the settings file and initializes the Datarecorder output file
        """
        self.settings.load_from_file(settings_file_to_load)
        self.millis = self.settings.write_interval

        self.share_settings(self.settings)
        self.initialize_file()
        self.settings.save_to_file(self.default_settings_file_location)


    def save_settings_to_file(self, file_to_save_in):
        """
        Save current settings to a file, including the current write-interval time
        """
        self.settings.write_interval = self.timer.interval()
        self.settings.save_to_file(file_to_save_in)

    def do(self):
        """
        This function is called every controller tick of this module
        """
        self._write()
        if self.trajectory_recorder.should_record_trajectory:
            self.trajectory_recorder.write_trajectory()

    def initialize(self):
        """
        This function is called before the module is started
        And every time the Initialize button is clicked in the JoanModuleDialog,
        - which calls the JoanModuleAction, which is inherited by DataRecorderAction -
        """
        try:
            self.settings.write_interval = self.timer.interval()

            self.settings.save_to_file(self.default_settings_file_location)
            self.share_settings(self.settings)

            self.initialize_file()
            self.state_machine.request_state_change(State.READY)

            # Try and get the current position of car if you want to record a trajectory
            self.trajectory_recorder.initialize_trajectory_recorder_variables()

        except RuntimeError:
            return False
        return True

    def stop(self):
        """
        Stops writing and closes the datawriter filehandle
        """
        super().stop()
        self.data_writer.close()
        self.state_machine.request_state_change(State.IDLE)

    def start(self):
        """
        Opens the datawriter
        """
        self.state_machine.request_state_change(State.RUNNING)
        self.data_writer.open(filename=self.get_filename())
        super().start()

    def _write(self):
        """
        Create a time-field with the current time and writes available news from all channels(=modules)
        """
        now = datetime.now()
        self.data_writer.write(timestamp=now, news=self.get_all_news(), channels=self.get_available_news_channels())

    def _create_filename(self, extension=''):
        """
        Create a filename where the name is a combination of the current date and time and the extension
        :param extension: extension that is added to the filename
        :return: the name of the file
        """
        now = datetime.now()
        now_string = now.strftime('%Y%m%d_%H%M%S')
        filename = '%s_%s' % ('data', now_string)
        if extension != '':
            extension = extension[0] == '.' or '.%s' % extension
            filename = '%s%s' % (filename, extension)
        return filename

    def get_filename(self):
        return self.filename

    def handle_dialog_checkboxes(self, checkbox_path):
        """
        Takes keys from a defined array, first one is the module-key
        last one is the new value
        This is done for every key, per key, which is a bit brute
        Settings in Datarecorder settings->variables_to_save are replaced with the new value
        This works because dict elements are actually pointers
        If no key exists, it will be added
        :param checkbox_path: a list, containing the selected item an its pedigree in reverse order
        """
        if self.settings.variables_to_save.get(checkbox_path[0]) is None:
            self.settings.variables_to_save[checkbox_path[0]] = {}
        temp_dict = self.settings.variables_to_save.get(checkbox_path[0])
        for key in checkbox_path[1:-2]:
            if temp_dict.get(key) is None:
                temp_dict[key] = {}
            temp_dict = temp_dict.get(key)
        temp_dict[checkbox_path[-2]] = checkbox_path[-1]
        # save the settings
        self.save_settings_to_file(self.default_settings_file_location)
        # share the settings
        self.share_settings(self.settings)

class Trajectory_recorder():
    def __init__(self, data_recorder_action, waypoint_distance):
        self._traveled_distance = 0
        self._overall_distance = 0
        self.data_recorder_action = data_recorder_action
        self.waypoint_distance = waypoint_distance

        self.should_record_trajectory = False

    def discard_current_trajectory(self):
        self._trajectory_data = None
        self._trajectory_data_spaced = None

    def make_trajectory_array(self, waypoint_distance):

        temp_diff = self._trajectory_data[-1] - self._trajectory_data[-2]

        position_difference = temp_diff[0:2]
        small_distance = np.linalg.norm(position_difference)
        self._overall_distance = self._overall_distance + small_distance
        self._traveled_distance = self._traveled_distance + small_distance

        if (self._overall_distance >= waypoint_distance):
            self._trajectory_data_spaced = np.append(self._trajectory_data_spaced, [self._trajectory_data[-1]], axis=0)
            self._overall_distance = self._overall_distance - waypoint_distance

    def trajectory_record_boolean(self, trajectory_boolean):
        self.should_record_trajectory = trajectory_boolean

    def generate_trajectory(self):
        # Add index nr to the trajectory
        indices = np.arange(len(self._trajectory_data_spaced))
        self._trajectory_data_spaced = np.insert(self._trajectory_data_spaced, 0, indices, axis=1)
        return self._trajectory_data_spaced

    def write_trajectory(self):
        _data = self.data_recorder_action.read_news(JOANModules.AGENT_MANAGER)
        car = _data['agents']['Car 1']['vehicle_object'].spawned_vehicle
        control = car.get_control()

        x_pos = car.get_transform().location.x
        y_pos = car.get_transform().location.y
        steering_wheel_angle = control.steer
        throttle_input = control.throttle
        brake_input = control.brake
        heading = car.get_transform().rotation.yaw
        vel = math.sqrt(car.get_velocity().x**2 + car.get_velocity().y**2 + car.get_velocity().z**2)

        self._trajectory_data = np.append(self._trajectory_data, [[x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading, vel]], axis=0)

        self.make_trajectory_array(self.waypoint_distance)

    def initialize_trajectory_recorder_variables(self):
        try:
            _data = self.data_recorder_action.read_news(JOANModules.AGENT_MANAGER)
            car = _data['agents']['Car 1']['vehicle_object'].spawned_vehicle
            control = car.get_control()

            x_pos = car.get_transform().location.x
            y_pos = car.get_transform().location.y
            steering_wheel_angle = control.steer
            throttle_input = control.throttle
            brake_input = control.brake
            heading = car.get_transform().rotation.yaw
            vel = math.sqrt(car.get_velocity().x ** 2 + car.get_velocity().y ** 2 + car.get_velocity().z ** 2)

            # initialize variables here because we want the current position as first entry!
            self._trajectory_data = [[x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading, vel]]
            self._trajectory_data_spaced = [[x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading, vel]]
        except Exception as inst:
            print(inst)
