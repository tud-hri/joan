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

        self.amount_of_remaining_points = 50
        self.history_time = self.amount_of_remaining_points / round(1000 / self._millis)
        self.plot_data_torque_x = []
        self.plot_data_torque_y = []
        self.plot_data_e_lat_y = [0] * self.amount_of_remaining_points
        self.plot_data_e_psi_y = [0] * self.amount_of_remaining_points
        self.plot_data_loha_y = [0] * self.amount_of_remaining_points
        self.plot_data_sw_des_y = [0] * self.amount_of_remaining_points
        self.plot_data_sw_act_y = [0] * self.amount_of_remaining_points

        self.labelfont = QtGui.QFont()
        self.labelfont.setPixelSize(20)

        length = self.amount_of_remaining_points
        lower = -self.history_time
        upper = 0
        self.time_list = [lower + x * (upper - lower) / length for x in range(length)]
        self.brushes = []
        self.pens = []
        colors_rgb = []
        red = Color("red")
        colors = list(red.range_to(Color("green"), self.amount_of_remaining_points))
        for color in colors:
            colors_rgb.append(color.rgb)

        background_color = pg.mkColor((240, 240, 240, 255))
        pg.setConfigOption('background', background_color)
        pg.setConfigOption('foreground', 'k')

        for k in range(self.amount_of_remaining_points):
            self.brushes.append(pg.mkBrush(round(256 * colors_rgb[k][0]), round(256 * colors_rgb[k][1]), round(256 * colors_rgb[k][2]), 255))
            self.pens.append(pg.mkPen(round(256 * colors_rgb[k][0]), round(256 * colors_rgb[k][1]), round(256 * colors_rgb[k][2]), 255))

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
        data_from_carla_interface = self.read_news(JOANModules.CARLA_INTERFACE)

        # try assigning variables:
        try:
            steering_ang = data_from_hardware_manager['SensoDrive 1']['steering_angle']
            req_torque = data_from_hardware_manager['SensoDrive 1']['measured_torque']
            sw_actual = data_from_hardware_manager['SensoDrive 1']['steering_angle']
        except KeyError or TypeError:
            steering_ang = 0
            req_torque = 0
            sw_actual = 0

        try:
            lat_error = data_from_sw_controller['FDCA 1']['lat_error']
            sw_des = data_from_sw_controller['FDCA 1']['sw_angle_desired_radians']
            heading_error = data_from_sw_controller['FDCA 1']['heading_error']
            loha = data_from_sw_controller['FDCA 1']['loha']

        except KeyError or TypeError:
            lat_error = 0
            sw_des = 0
            heading_error = 0
            loha = 0

        # Torque plot
        self.plot_data_torque_x.append(steering_ang)
        self.plot_data_torque_y.append(req_torque)
        if len(self.plot_data_torque_x) > self.amount_of_remaining_points:
            self.plot_data_torque_y.pop(0)
            self.plot_data_torque_x.pop(0)
            self.torque_plot_handle.setData(x=self.plot_data_torque_x, y=self.plot_data_torque_y, size=10, pen=pg.mkPen((0, 0, 0, 200)), brush='g', symbol='d',
                                            symbolBrush=self.brushes, symbolPen=self.pens, symbolSize=10)

        # E_lat plot
        self.plot_data_e_lat_y.append(lat_error)
        self.plot_data_e_lat_y.pop(0)
        self.e_lat_plot_handle.setData(x=self.time_list, y=self.plot_data_e_lat_y, size=2, pen=pg.mkPen((0, 0, 0, 200)), brush='g', symbol='d', symbolBrush=self.brushes,
                                       symbolPen=self.pens, symbolSize=5)

        # E_psi plot
        self.plot_data_e_psi_y.append(heading_error)
        self.plot_data_e_psi_y.pop(0)
        self.e_psi_plot_handle.setData(x=self.time_list, y=self.plot_data_e_psi_y, size=2, pen=pg.mkPen((0, 0, 0, 200)), brush='g', symbol='d', symbolBrush=self.brushes,
                                       symbolPen=self.pens, symbolSize=5)

        # loha Plot
        self.plot_data_loha_y.append(loha)
        self.plot_data_loha_y.pop(0)
        self.loha_plot_handle.setData(x=self.time_list, y=self.plot_data_loha_y, size=2, pen=pg.mkPen((0, 0, 0, 200)), brush='g', symbol='d', symbolBrush=self.brushes,
                                      symbolPen=self.pens, symbolSize=5)

        # sw desired plot
        self.plot_data_sw_des_y.append(sw_des)
        self.plot_data_sw_des_y.pop(0)
        self.sw_des_plot_handle.setData(x=self.time_list, y=self.plot_data_sw_des_y, size=2, pen=pg.mkPen((0, 0, 0, 200)), brush='g', symbol='d', symbolBrush=self.brushes,
                                        symbolPen=self.pens, symbolSize=5)

        # sw actual plot
        # sw desired plot
        self.plot_data_sw_act_y.append(sw_actual)
        self.plot_data_sw_act_y.pop(0)
        self.sw_act_plot_handle.setData(x=self.time_list, y=self.plot_data_sw_act_y, size=2, pen=pg.mkPen((0, 0, 0, 200)), brush='g', symbol='d', symbolBrush=self.brushes,
                                        symbolPen=self.pens, symbolSize=5)

    def initialize(self):
        """
        This function is called before the module is started
        """
        # This is de place to do all initialization needed. In the example here, the necessary settings are copied from the settings object.
        # This is done during the initialization to prevent settings from changing while the module is running. This does mean that the module needs to be
        # reinitialised every time the settings are changed.
        self.data['counter'] = self.counter
        self.write_news(news=self.data)

        styles = {'font-size': '20px'}

        self.torque_plot_handle = self.module_dialog.module_widget.torque_graph.plot()
        self.e_lat_plot_handle = self.module_dialog.module_widget.lat_e_graph.plot()
        self.e_psi_plot_handle = self.module_dialog.module_widget.psi_e_graph.plot()
        self.loha_plot_handle = self.module_dialog.module_widget.loha_graph.plot()
        self.sw_des_plot_handle = self.module_dialog.module_widget.sw_des_graph.plot()
        self.sw_act_plot_handle = self.module_dialog.module_widget.sw_actual_graph.plot()

        ## Initialize Torque Graph
        self.module_dialog.module_widget.torque_graph.setXRange(-4 * math.pi, 4 * math.pi, padding=0)
        self.module_dialog.module_widget.torque_graph.setYRange(-15, 15, padding=0)
        self.module_dialog.module_widget.torque_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.torque_graph.setTitle('Steering Angle vs Torque')
        self.module_dialog.module_widget.torque_graph.setLabel('left', 'Torque [Nm]', **styles)
        self.module_dialog.module_widget.torque_graph.setLabel('bottom', '<font>&Theta;SW</font> [rad]', **{'font-size': '20pt'})
        self.module_dialog.module_widget.torque_graph.getAxis('bottom').setTickFont(self.labelfont)
        self.module_dialog.module_widget.torque_graph.getAxis("bottom").setStyle(tickTextOffset=20)
        self.module_dialog.module_widget.torque_graph.getAxis('left').setTickFont(self.labelfont)
        self.module_dialog.module_widget.torque_graph.getAxis("left").setStyle(tickTextOffset=20)
        torque_viewbox = self.module_dialog.module_widget.torque_graph.getViewBox()
        torque_viewbox.invertX(True)
        torque_viewbox.setBackgroundColor((255, 255, 255, 200))

        ## Initialize lat Error Plot
        self.module_dialog.module_widget.lat_e_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.lat_e_graph.setYRange(-8, 8, padding=0)
        self.module_dialog.module_widget.lat_e_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.lat_e_graph.setLabel('right', 'e<sub>lat</sub> [m]', **{'font-size': '14pt'})
        lat_error_viewbox = self.module_dialog.module_widget.lat_e_graph.getViewBox()
        lat_error_viewbox.setBackgroundColor((255, 255, 255, 200))

        ## Initialize heading Error Plot
        self.module_dialog.module_widget.psi_e_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.psi_e_graph.setYRange(-math.pi, math.pi, padding=0)
        self.module_dialog.module_widget.psi_e_graph.setLabel('right', 'e<sub><font>&Psi;</font></sub> [rad]', **{'font-size': '14pt'})
        psi_error_viewbox = self.module_dialog.module_widget.psi_e_graph.getViewBox()
        psi_error_viewbox.setBackgroundColor((255, 255, 255, 200))
        self.module_dialog.module_widget.psi_e_graph.showGrid(True, True, 1)

        ## Initialize level of haptic authority (LOHA) Plot
        self.module_dialog.module_widget.loha_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.loha_graph.setYRange(-1, 11, padding=0)
        self.module_dialog.module_widget.loha_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.loha_graph.setLabel('right', 'LoHA [Nm/rad]', **{'font-size': '14pt'})
        loha_viewbox = self.module_dialog.module_widget.loha_graph.getViewBox()
        loha_viewbox.setBackgroundColor((255, 255, 255, 200))

        ## Initialize sw angle desired Plot
        self.module_dialog.module_widget.sw_des_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.sw_des_graph.setYRange(-math.pi, math.pi, padding=0)
        self.module_dialog.module_widget.sw_des_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.sw_des_graph.setLabel('right', '<font>&Theta;SW</font><sub>des</sub> [rad]', **{'font-size': '14pt'})
        sw_des_viewbox = self.module_dialog.module_widget.sw_des_graph.getViewBox()
        sw_des_viewbox.setBackgroundColor((255, 255, 255, 200))

        ## Initialize sw angle actual plot
        self.module_dialog.module_widget.sw_actual_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.sw_actual_graph.setYRange(-math.pi, math.pi, padding=0)
        self.module_dialog.module_widget.sw_actual_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.sw_actual_graph.setLabel('right', '<font>&Theta;SW</font><sub>act</sub> [rad]', **{'font-size': '14pt'})
        self.module_dialog.module_widget.sw_actual_graph.setLabel('bottom', 'Time[s]', **{'font-size': '14pt'})

        sw_actual_viewbox = self.module_dialog.module_widget.sw_actual_graph.getViewBox()
        sw_actual_viewbox.setBackgroundColor((255, 255, 255, 200))

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
        self.module_dialog.module_widget.torque_graph.clear()
        self.module_dialog.module_widget.lat_e_graph.clear()
        self.module_dialog.module_widget.psi_e_graph.clear()
        self.module_dialog.module_widget.loha_graph.clear()
        self.module_dialog.module_widget.sw_des_graph.clear()
        self.module_dialog.module_widget.sw_actual_graph.clear()

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
