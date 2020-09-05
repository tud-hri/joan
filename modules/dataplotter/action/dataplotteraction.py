import os
from pathlib import Path
from datetime import datetime

from modules.dataplotter.action.dataplotter import DataPlotter
from modules.dataplotter.action.dataplottersettings import DataPlotterSettings
from modules.joanmodules import JOANModules

from core.joanmoduleaction import JoanModuleAction
from core.statesenum import State
from core.status import Status


class DataplotterAction(JoanModuleAction):
    """
    Does all kinds of action concerning the Dataplotter module
    Inherits actions from the JoanModuleActions
    """

    def __init__(self, millis=20):
        """
        :param millis: contains the value of the writing interval
        """
        super().__init__(module=JOANModules.DATA_PLOTTER, millis=millis)

        # start settings for this module
        self.settings = DataPlotterSettings(JOANModules.DATA_PLOTTER)
        self.default_settings_file_location = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                           'dataplottersettings.json')

        if Path(self.default_settings_file_location).is_file():
            self._load_settings_from_file(self.default_settings_file_location)
            self.millis = self.settings.write_interval
        else:
            self.settings.set_all_empty()
            self.settings.write_interval = 100
            self.save_settings_to_file(self.default_settings_file_location)

        self.share_settings(self.settings)
        # end settings for this module

        self.filename = ''
        self.data_plotter = DataPlotter(news=self.get_all_news(),
                                        channels=self.get_available_news_channels(),
                                        settings=self.get_module_settings(JOANModules.DATA_PLOTTER))

        # TODO: run data_plotter in separate thread
        # self.data_plotter.start()

    def _load_settings_from_file(self, settings_file_to_load):
        """
        Loads the settings file for the Datarecorder and saves these settings in the default settings file location
        Sets the write interval from the settings file and initializes the Datarecorder output file
        """
        self.settings.load_from_file(settings_file_to_load)
        self.millis = self.settings.write_interval

        self.share_settings(self.settings)
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
        self._plot()

    def initialize(self):
        """
        This function is called before the module is started
        And every time the Initialize button is clicked in the JoanModuleDialog,
        - which calls the JoanModuleAction, which is inherited by DataPlotterAction -
        """
        try:
            self.settings.write_interval = self.timer.interval()

            # renew settings
            self.settings.refresh(self.settings.as_dict().get(str(JOANModules.DATA_PLOTTER)).get('variables_to_save'))

            self.settings.save_to_file(self.default_settings_file_location)
            self.share_settings(self.settings)

            self.state_machine.request_state_change(State.READY)

        except RuntimeError:
            return False
        return True

    def stop(self):
        """
        Stops writing and closes the datawriter filehandle
        """
        super().stop()
        # TODO: make plot class: self.data_plotter.close()
        self.state_machine.request_state_change(State.IDLE)

    def start(self):
        """
        Opens the dataplotter
        """
        self.state_machine.request_state_change(State.RUNNING)
        self.data_plotter.set_window()
        super().start()

    def load_settings(self, settings_file_to_load):
        self._load_settings_from_file(settings_file_to_load)
        self.state_machine.request_state_change(State.READY)

    def _plot(self):
        """
        Create a time-field with the current time and plots available news from all channels(=modules)
        according to the plottersettings
        """
        now = datetime.now()
        self.data_plotter.write(timestamp=now, news=self.get_all_news(), channels=self.get_available_news_channels())
        # TODO: create the plotter class

    def handle_tree_widget_click(self):
        """
        Saves settings, as changed/set in the DataPlotterDialog/CreateTreeWidgetDialog class
        Share the new settings in the Settings singleton
        """
        # save the settings
        self.save_settings_to_file(self.default_settings_file_location)
        # share the settings
        self.share_settings(self.settings)
