import os
from datetime import datetime
from pathlib import Path

from modules.datarecorder.action.datarecordersettings import DataRecorderSettings
from modules.datarecorder.action.datarecordersignals import DataRecorderSignals
from modules.datarecorder.action.datawriter import DataWriter
from modules.datarecorder.action.trajectoryrecorder import TrajectoryRecorder
from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State


def _create_filename(extension=''):
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


class DataRecorderAction(JoanModuleAction):
    """
    Does all kinds of action concerning the Datarecorder module
    Inherits actions from the JoanModuleActions
    """

    def __init__(self, millis=20):
        """
        :param millis: contains the value of the writing interval
        """
        super().__init__(module=JOANModules.DATA_RECORDER, millis=millis)

        # trajectory recorder:
        self.trajectory_recorder = TrajectoryRecorder(self, 0.1)

        # start settings for this module
        self.settings = DataRecorderSettings(JOANModules.DATA_RECORDER)
        self.default_settings_file_location = os.path.join(self.module_path, 'action', 'default_settings.json')

        if Path(self.default_settings_file_location).is_file():
            self._load_settings_from_file(self.default_settings_file_location)
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

        # TODO: run data_writer in separate process (multiprocess)
        # self.data_writer.start()

        # signals and slots
        self._module_signals = DataRecorderSignals(self.module, self)
        self.singleton_signals.add_signals(self.module, self._module_signals)

        self._module_signals.prepare_recording.connect(self.initialize)
        self._module_signals.start_recording.connect(self.start)
        self._module_signals.stop_recording.connect(self.stop)

    def initialize_file(self):
        """
        Creates a filename with extension
        """
        self.filename = _create_filename(extension='csv')

    def _load_settings_from_file(self, settings_file_to_load):
        """
        Loads the settings file for the Datarecorder and saves these settings in the default settings file location
        Sets the write interval from the settings file and initializes the Datarecorder output file
        """
        self.settings.load_from_file(settings_file_to_load)
        self.millis = self.settings.write_interval

        self.share_settings(self.settings)
        self.initialize_file()
        self.settings.save_to_file(self.default_settings_file_location)

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

            # renew settings
            self.settings.refresh(self.settings.as_dict().get(str(JOANModules.DATA_RECORDER)).get('variables_to_save'))

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
        self.data_writer.open(filename=self.get_filename(), filepath='datalogs')
        super().start()

    def _write(self):
        """
        Create a time-field with the current time and writes available news from all channels(=modules)
        """
        now = datetime.now()
        self.data_writer.write(timestamp=now, news=self.get_all_news(), channels=self.get_available_news_channels())

    def load_settings(self, settings_file_to_load):
        self._load_settings_from_file(settings_file_to_load)
        self.state_machine.request_state_change(State.READY)

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

        # save the settings - DEPRECATED; settings are only saved when the user explicitly wants to.
        # self.save_settings_to_file(self.default_settings_file_location)
        # share the settings
        # self.share_settings(self.settings)
