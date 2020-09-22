"""
TemplateAction class

This is a template for creating new JOAN modules
We tried to explain how a module works through the comments and
will keep adding explanation as new functionality is added to the module

"""
import os

from PyQt5 import QtCore, QtGui


from modules.joanmodules import JOANModules
from core.joanmoduleaction import JoanModuleAction
from core.statesenum import State
from .controllerplottersettings import ControllerPlotterSettings
import math
import pyqtgraph as pg
import numpy as np
from colour import Color




class ControllerPlotterAction(JoanModuleAction):
    """Example JOAN module"""

    def __init__(self, millis=10):
        super().__init__(module=JOANModules.CONTROLLER_PLOTTER, millis=millis)




        # Finally it is also possible to define automatic state changes. If state A is entered and the transition to state B is immediately legal, the state
        # machine will automatically progress to state B. It is possible to define one automatic state change per state, except for the Error state. It is
        # illegal to automatically leave the Error state for safety reasons. Not that state A wil not be skipped, but exited automatically. So the state changes
        # are subject to all normal conditions and entry and exit actions.
        # Note: This means that a transition condition must be defined!


        # start news for the datarecorder.
        # here, we are added a variable called 'datawriter output' to this modules News.
        # You can choose your own variable names and you can add as many vairables to self.data as you want.
        self.data['datawriter output'] = 2020
        self.data['nesting'] = {'example 1': 44, 'example 2': 35}
        self.counter = 0  # see def do(self):
        self.sign = 1  # see def do(self):
        self.write_news(news=self.data)
        self.time = QtCore.QTime()
        self.plotpoints = []
        self.amount_of_remaining_points = 100
        self.plot_data_torque_x= np.array([])
        self.plot_data_torque_y = np.array([])
        self.plot_data_e_lat_y = np.zeros(100)
        self.time_vector = np.linspace(-10, 0, 100)

        # end news for the datarecorder

        self.brushes = []
        self.pens = []
        colors_rgb = []
        red = Color("red")
        colors = list(red.range_to(Color("green"),self.amount_of_remaining_points))
        for color in colors:
            colors_rgb.append(color.rgb)

        background_color = pg.mkColor((240, 240, 240, 255))
        pg.setConfigOption('background', background_color)
        pg.setConfigOption('foreground', 'k')


        for k in range(self.amount_of_remaining_points):
            self.brushes.append(pg.mkBrush(round(256 * colors_rgb[k][0]), round(256 * colors_rgb[k][1]), round(256 * colors_rgb[k][2]), k*2))
            self.pens.append(pg.mkPen(round(256 * colors_rgb[k][0]), round(256 * colors_rgb[k][1]), round(256 * colors_rgb[k][2]), k*2))



        # start settings for this module
        # each module has its own settings, which are stored in a .json file (e.g. template_settings.json)
        # To create settings for your custom module create a settings class and enherit JOANMOduleSetting, as in the example TempleSettings
        # All attributes you add to your settings class will automatically be save if you call setting.save_to_file
        # when loading setting, all attribute in the JSON file are copied, but missing values will keep their default value as defined in your setting class

        # first create a settings object containing the default values
        self.settings = ControllerPlotterSettings(module_enum=JOANModules.CONTROLLER_PLOTTER)

        # then load the saved value from a file, this can be done here, or implement a button with which the user can specify the file to load from.
        default_settings_file_location = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                      'template_settings.json')
        if os.path.isfile(default_settings_file_location):
            self.settings.load_from_file(default_settings_file_location)

        # now you can copy the current settings as attributes of the action class, but please note that it is also possible to access the settings directly.
        self.millis = self.settings.millis

        # finale update the new setting to the settings singleton (such that other modules can also see this module's settings)
        self.share_settings(self.settings)
        # end settings for this module



    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """

        data_from_sw_controller = self.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        data_from_hardware_manager = self.read_news(JOANModules.HARDWARE_MANAGER)

        # try assigning variables:
        try:
            steering_ang = data_from_hardware_manager['SensoDrive 1']['steering_angle']
            req_torque = data_from_hardware_manager['SensoDrive 1']['measured_torque']

            lat_error = data_from_sw_controller['FDCA 1']['lat_error']
        except KeyError:
            steering_ang = 0
            req_torque = 0
            lat_error = 0

        self.torque_plot_handle = self.module_dialog.module_widget.torque_graph.plot()
        # self.e_lat_plot_handle = self.module_dialog.module_widget.lat_e_graph.plot()

        #Torque plot
        self.plot_data_torque_x = np.append(self.plot_data_torque_x, steering_ang)
        self.plot_data_torque_y = np.append(self.plot_data_torque_y, req_torque)
        if len(self.plot_data_torque_x) > self.amount_of_remaining_points:
            self.plot_data_torque_y = np.delete(self.plot_data_torque_y, 0)
            self.plot_data_torque_x = np.delete(self.plot_data_torque_x, 0)
            self.torque_plot_handle.setData(x=self.plot_data_torque_x, y=self.plot_data_torque_y, size=10, pen=pg.mkPen(None), brush='g', symbol='o', symbolBrush=self.brushes, symbolPen= self.pens)
            plot_points_torque = self.module_dialog.module_widget.torque_graph.listDataItems()
            self.module_dialog.module_widget.torque_graph.removeItem(plot_points_torque[0])

        #Elat plot
        self.plot_data_e_lat_y = np.append(self.plot_data_e_lat_y, lat_error)
        self.plot_data_e_lat_y = np.delete(self.plot_data_e_lat_y, 0)

        # print(self.plot_data_e_lat_y)
        self.module_dialog.module_widget.lat_e_graph.clear()
        self.module_dialog.module_widget.lat_e_graph.plot(x=self.time_vector, y=self.plot_data_e_lat_y, size=10, pen=pg.mkPen(None), brush='g', symbol='o', symbolBrush=self.brushes, symbolPen= self.pens)
        # plot_points_e_lat = self.module_dialog.module_widget.lat_e_graph.listDataItems()
        # self.module_dialog.module_widget.lat_e_graph.removeItem(plot_points_e_lat[1:])

        # print(len(self.plot_data_e_lat_y))

    def initialize(self):
        """
        This function is called before the module is started
        """
        # This is de place to do all initialization needed. In the example here, the necessary settings are copied from the settings object.
        # This is done during the initialization to prevent settings from changing while the module is running. This does mean that the module needs to be
        # reinitialised every time the settings are changed.
        self.data['counter'] = self.counter
        self.write_news(news=self.data)
        self.e_lat_plot_handle = self.module_dialog.module_widget.lat_e_graph.plot()

        ## Initialize Torque Graph
        self.module_dialog.module_widget.torque_graph.setXRange(-2 * math.pi, 2 * math.pi, padding=0)
        self.module_dialog.module_widget.torque_graph.setYRange(-15, 15, padding=0)
        self.module_dialog.module_widget.torque_graph.showGrid(True,True, 1)
        self.module_dialog.module_widget.torque_graph.setTitle('Torque vs Steering Angle', fontsize = 10)
        self.module_dialog.module_widget.torque_graph.setLabel('left', 'Torque [Nm]')
        self.module_dialog.module_widget.torque_graph.setLabel('bottom', 'Steering Angle [rad]')
        torque_viewbox = self.module_dialog.module_widget.torque_graph.getViewBox()
        torque_viewbox.setBackgroundColor((255,255,255,200))

        ## Initialize Lat Error Plot
        self.module_dialog.module_widget.lat_e_graph.setXRange(-10, 2, padding=0)
        self.module_dialog.module_widget.lat_e_graph.setYRange(-10, 10, padding=0)
        self.module_dialog.module_widget.lat_e_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.lat_e_graph.setLabel('left', 'Lat Error [m]')
        lat_error_viewbox = self.module_dialog.module_widget.lat_e_graph.getViewBox()
        lat_error_viewbox.setBackgroundColor((255, 255, 255, 200))





        self.millis = self.settings.millis

        # if (self.state_machine.current_state is State.IDLE):
        self.state_machine.request_state_change(State.READY)  # , "You can now start the module")
        # elif (self.state_machine.current_state is State.ERROR):
        #    self.state_machine.request_state_change(State.IDLE)



        return super().initialize()

    def start(self):
        """start the module"""
        self.state_machine.request_state_change(target_state=State.RUNNING)
        return super().start()

    def stop(self):
        """stop the module"""
        # Will automatically go to READY as defined above in self.state_machine.set_automatic_transition
        self.state_machine.request_state_change(State.IDLE)

        return super().stop()

    def _starting_condition(self):
        """
        This is an example of a transition condition for the state machine. If this condition is true, the transition to the running state is allowed. Also
        check the setting of this condition in the constructor of this class.

        :return: (bool) legality of state change, (str) error message
        """
        try:
            return True, ''

        except KeyError:
            return False, 'The hardware manager state could not be read, but it should be running before starting template.'

    def _clean_up_after_run(self):
        """
        This is an example of an exit action for a state, if the running state is exited, this function is executed. This can be used to clean up connections,
        close files or do other final actions. Also check the setting of this action in the constructor of this class. Please note that this action is always
        called, no matter the target state after the state change. It can be compared with the finally statement in exeption handling.
        :return: None
        """
        # do some interesting multi line cleaning up of the mess I made during execution.
        pass

    def _execute_on_state_change_in_module_action_1(self):
        # example of adding a method to be executed on a state change request
        pass

    def _execute_on_state_change_in_module_action_2(self):
        # example of adding a method to be executed on a state change request
        pass
