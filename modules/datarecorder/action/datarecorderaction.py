from datetime import datetime
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from modules.datarecorder.action.states import DatarecorderStates
from modules.datarecorder.action.datawriter import DataWriter
from process.settings import ModuleSettings
from .datarecordersettings import DataRecorderSettings

# for editWidgets
from PyQt5 import QtWidgets, QtGui
from functools import partial
import os
import numpy as np


class DatarecorderAction(JoanModuleAction):
    def __init__(self, millis=200):
        super().__init__(module=JOANModules.DATA_RECORDER, millis=millis)
        # def __init__(self, master_state_handler, millis=200):
        #    super().__init__(module=JOANModules.DATA_RECORDER, master_state_handler=master_state_handler, millis=millis)
        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.NOTINITIALIZED)

        # next three Template lines are not used for datarecorder' 
        # 1. self.data['t'] = 0
        # 2. self.write_news(news=self.data)
        # 3. self.time = QtCore.QTime()

        # trajectory recorder:
        self.trajectory_recorder = Trajectory_recorder(self, 0.1)

        # start settings for this module
        self.settings = DataRecorderSettings(JOANModules.DATA_RECORDER)
        default_settings_file_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'datarecordersettings.json')
        if os.path.isfile(default_settings_file_location):
            self.settings.load_from_file(default_settings_file_location)

        self.share_settings(self.settings)
        # end settings for this module

        self.filename = ''
        self.data_writer = DataWriter(news=self.get_all_news(), channels=self.get_available_news_channels(),
                                      settings=self.get_module_settings(JOANModules.DATA_RECORDER))

    def initialize_file(self):
        self.initialize()
        self.filename = self._create_filename(extension='csv')
        return True

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        self._write()
        if self.trajectory_recorder.should_record_trajectory:
            self.trajectory_recorder.write_trajectory()

        # next two Template lines are not used for datarecorder
        # 1. self.data['t'] = self.time.elapsed()
        # 2. self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        try:
            self.module_state_handler.request_state_change(DatarecorderStates.INIT.INITIALIZING)
            print('datarecorderaction initialize started')
            # Try and get the current position of car if you want to record a trajectory
            self.trajectory_recorder.initialize_trajectory_recorder_variables()

        except RuntimeError:
            return False
        return True

    def stop(self):
        """
        Close the threaded filehandle(s)
        """
        super().stop()
        self.data_writer.close()
        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.STOP)

    def start(self):
        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.START)
        self.data_writer.open(filename=self.get_filename())
        super().start()

    def _write(self):
        now = datetime.now()
        self.data_writer.write(timestamp=now, news=self.get_all_news(), channels=self.get_available_news_channels())

    def _create_filename(self, extension=''):
        now = datetime.now()
        now_string = now.strftime('%Y%m%d_%H%M%S')
        filename = '%s_%s' % ('data', now_string)
        if extension != '':
            extension = extension[0] == '.' or '.%s' % extension
            filename = '%s%s' % (filename, extension)
        return filename

    def get_filename(self):
        return self.filename

    def _editWidget(self, layout=None):
        content = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(content)

        # cleanup previous widgets from scroll area
        for i in reversed(range(vlay.count())):
            marked_widget = vlay.takeAt(i).widget()
            vlay.removeWidget(marked_widget)
            marked_widget.setParent(None)
        # cleanup previous widgets from verticalLayout_items
        for i in reversed(range(layout.count())):
            marked_widget = layout.takeAt(i).widget()
            layout.removeWidget(marked_widget)
            marked_widget.setParent(None)
        scroll = QtWidgets.QScrollArea()
        layout.addWidget(scroll)
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)

        label_font = QtGui.QFont()
        label_font.setPointSize(12)
        item_font = QtGui.QFont()
        item_font.setPointSize(10)
        news_checkbox = {}
        # module_key = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        module_key = JOANModules.DATA_RECORDER
        item_widget = {}

        for channel in self.get_available_news_channels():
            if channel != module_key:
                if channel.name not in self.settings.variables_to_save.keys():
                    self.settings.variables_to_save.update({channel.name: {}})
                # news_checkbox[channel] = QtWidgets.QLabel(channel.split('.')[1])
                news_checkbox[channel.name] = QtWidgets.QLabel(channel.name)
                news_checkbox[channel.name].setFont(label_font)
                news = self.read_news(channel)
                if news:
                    vlay.addWidget(news_checkbox[channel.name])

                    for item in news:
                        item_widget[item] = QtWidgets.QCheckBox(item)
                        item_widget[item].setFont(item_font)
                        # lambda will not deliver what you expect:
                        # item_widget[item].clicked.connect(lambda:
                        #                                  self.handlemodulesettings(item_widget[item].text(),
                        #                                  item_widget[item].isChecked()))
                        item_widget[item].stateChanged.connect(lambda: self._handle_module_settings(channel.name, item_widget[item]))
                        vlay.addWidget(item_widget[item])

                        # start set checkboxes from current_settings
                        if item not in self.settings.variables_to_save[channel.name].keys():
                            item_widget[item].setChecked(True)
                            item_widget[item].stateChanged.emit(True)
                        else:
                            item_widget[item].setChecked(self.settings.variables_to_save[channel.name][item])
                            item_widget[item].stateChanged.emit(self.settings.variables_to_save[channel.name][item])
                        # end set checkboxes from current_settings

        vlay.addStretch()

        content.adjustSize()

    def _handle_module_settings(self, module_key, item):
        self.settings.variables_to_save[module_key][item.text()] = item.isChecked()

    def _clicked_btn_initialize(self):
        """initialize the data recorder (mainly setting the data directory and data file prefix"""
        self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.INITIALIZING)
        self.share_settings(self.settings)

        if self.initialize_file():
            self.module_state_handler.request_state_change(DatarecorderStates.DATARECORDER.INITIALIZED)


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
        _data = self.data_recorder_action.read_news(JOANModules.CARLA_INTERFACE)
        car = _data['vehicles'][0].spawned_vehicle
        control = car.get_control()

        x_pos = car.get_transform().location.x
        y_pos = car.get_transform().location.y
        steering_wheel_angle = control.steer
        throttle_input = control.throttle
        brake_input = control.brake
        heading = car.get_transform().rotation.yaw

        self._trajectory_data = np.append(self._trajectory_data, [[x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading]], axis=0)

        self.make_trajectory_array(self.waypoint_distance)

    def initialize_trajectory_recorder_variables(self):
        try:
            _data = self.data_recorder_action.read_news(JOANModules.CARLA_INTERFACE)
            car = _data['vehicles'][0].spawned_vehicle
            control = car.get_control()

            x_pos = car.get_transform().location.x
            y_pos = car.get_transform().location.y
            steering_wheel_angle = control.steer
            throttle_input = control.throttle
            brake_input = control.brake
            heading = car.get_transform().rotation.yaw

            # initialize variables here because we want the current position as first entry!
            self._trajectory_data = [[x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading]]
            self._trajectory_data_spaced = [[x_pos, y_pos, steering_wheel_angle, throttle_input, brake_input, heading]]
        except Exception as inst:
            print(inst)
