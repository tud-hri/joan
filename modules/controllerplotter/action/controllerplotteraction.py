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
import pandas as pd
import numpy as np


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
        self.car_trace_length = 10
        self.history_time = self.amount_of_remaining_points / round(1000 / self._millis)
        self.plot_data_torque_x = []
        self.plot_data_torque_y = []
        self.plot_data_e_lat_y = [0] * self.amount_of_remaining_points
        self.plot_data_e_psi_y = [0] * self.amount_of_remaining_points
        self.plot_data_fb_torque_y = [0] * self.amount_of_remaining_points
        self.plot_data_ff_torque_y = [0] * self.amount_of_remaining_points
        self.plot_data_loha_torque_y = [0] * self.amount_of_remaining_points
        self.plot_data_total_torque_y = [0] * self.amount_of_remaining_points
        self.plot_data_loha_y = [0] * self.amount_of_remaining_points
        self.plot_data_sw_des_y = [0] * self.amount_of_remaining_points
        self.plot_data_sw_act_y = [0] * self.amount_of_remaining_points
        self.plot_data_road_x = []
        self.plot_data_road_x_outer = []
        self.plot_data_road_x_inner = []
        self.plot_data_road_y = []
        self.plot_data_road_y_outer = []
        self.plot_data_road_y_inner = []
        self.plot_data_road_psi = []
        self.plot_data_road_psi_deg = []
        self.road_lanewidth = []
        self.car_trace_x = [0] * self.car_trace_length
        self.car_trace_y = [0] * self.car_trace_length
        self.car_trace_psi = [0] * self.car_trace_length
        self.plot_data_sw_stiffness_x = [-160, 160]
        self.plot_data_sw_stiffness_y = [0, 0]
        self.converted_x_road_outer = [] * 50
        self.converted_y_road_outer = [] * 50

        self.labelfont = QtGui.QFont()
        self.labelfont.setPixelSize(14)

        length = self.amount_of_remaining_points
        lower = -self.history_time
        upper = 0
        self.time_list = [lower + x * (upper - lower) / length for x in range(length)]
        self.time_list_double = self.time_list + self.time_list
        self.brushes = []
        self.car_brushes = []
        self.pens = []
        self.car_pens = []
        colors_rgb = []
        colors_rgb_car = []
        red = Color("red")
        colors = list(red.range_to(Color("green"), self.amount_of_remaining_points))
        colors_car = list(red.range_to(Color("green"), self.car_trace_length))
        for color in colors:
            colors_rgb.append(color.rgb)

        for color_car in colors_car:
            colors_rgb_car.append(color_car.rgb)
        background_color = pg.mkColor((240, 240, 240, 255))
        pg.setConfigOption('background', background_color)
        pg.setConfigOption('foreground', 'k')

        for k in range(self.amount_of_remaining_points):
            self.brushes.append(
                pg.mkBrush(round(256 * colors_rgb[k][0]), round(256 * colors_rgb[k][1]), round(256 * colors_rgb[k][2]),
                           k * 3))
            self.pens.append(
                pg.mkPen(round(256 * colors_rgb[k][0]), round(256 * colors_rgb[k][1]), round(256 * colors_rgb[k][2]),
                         k * 3))

        for k in range(self.car_trace_length):
            self.car_brushes.append(
                pg.mkBrush(round(256 * colors_rgb_car[k][0]), round(256 * colors_rgb_car[k][1]), round(256 * colors_rgb_car[k][2]),
                           k * 25))
            self.car_pens.append(
                pg.mkPen((round(256 * colors_rgb[k][0]), round(256 * colors_rgb[k][1]), round(256 * colors_rgb[k][2]),
                          k * 25), width=3))

        self.double_pens = self.pens + self.pens
        self.double_brushes = self.brushes + self.brushes

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
        # from hardware manager
        try:
            if 'SensoDrive 1' in data_from_hardware_manager.keys():
                ## sensodrive
                steering_ang = math.degrees(data_from_hardware_manager['SensoDrive 1']['steering_angle'])
                actual_torque = data_from_hardware_manager['SensoDrive 1']['measured_torque']
                sw_actual = math.degrees(data_from_hardware_manager['SensoDrive 1']['steering_angle'])
                sw_stiffness = math.radians(data_from_hardware_manager['SensoDrive 1']['spring_stiffness'])
            elif 'Joystick 1' in data_from_hardware_manager.keys():
                ## joystick
                steering_ang = math.degrees(data_from_hardware_manager['Joystick 1']['steering_angle'])
                sw_actual = math.degrees(data_from_hardware_manager['Joystick 1']['steering_angle'])
            elif 'Keyboard 1' in data_from_hardware_manager.keys():
                ## keyboard
                steering_ang = math.degrees(data_from_hardware_manager['Keyboard 1']['steering_angle'])
                sw_actual = math.degrees(data_from_hardware_manager['Keyboard 1']['steering_angle'])
            else:
                steering_ang = 0
                sw_actual = 0
                sw_stiffness = 0

        except KeyError or TypeError:
            steering_ang = 0
            # req_torque = 0
            sw_actual = 0
            sw_stiffness = math.radians(1)

        # from steeringwheel controller
        try:
            lat_error = data_from_sw_controller['FDCA 1']['lat_error']
            sw_des = math.degrees(data_from_sw_controller['FDCA 1']['sw_angle_desired_radians'])
            heading_error = math.degrees(data_from_sw_controller['FDCA 1']['heading_error'])
            loha = math.radians(data_from_sw_controller['FDCA 1']['loha'])
            ff_torque = data_from_sw_controller['FDCA 1']['ff_torque']
            fb_torque = data_from_sw_controller['FDCA 1']['fb_torque']
            loha_torque = data_from_sw_controller['FDCA 1']['loha_torque']
            req_torque = data_from_sw_controller['FDCA 1']['sw_torque']


        except KeyError or TypeError:
            lat_error = 0
            sw_des = 0
            heading_error = 0
            loha = 0
            req_torque = 0
            fb_torque = 0
            ff_torque = 0
            loha_torque = 0

        # from carla interface
        try:
            vehicle_object = data_from_carla_interface['ego_agents']['EgoVehicle 1']['vehicle_object']
        except:
            vehicle_object = None

        # Top view plot
        if vehicle_object is not None:
            if vehicle_object.spawned_vehicle is not None:
                vehicle_location = vehicle_object.spawned_vehicle.get_location()
                closest_waypoint = data_from_carla_interface['map'].get_waypoint(vehicle_location, project_to_road=True)
                vehicle_rotation = vehicle_object.spawned_vehicle.get_transform().rotation.yaw

                # previous points
                previous_waypoints = []
                for a in reversed(range(1, 26)):
                    previous_waypoints.append(closest_waypoint.previous(a))

                # next
                next_waypoints = []
                for a in range(1, 26):
                    next_waypoints.append(closest_waypoint.next(a))

                for waypoints in previous_waypoints:
                    self.plot_data_road_x.append(waypoints[0].transform.location.x)
                    self.plot_data_road_y.append(waypoints[0].transform.location.y)
                    # self.plot_data_road_psi.append(waypoints[0].transform.rotation.yaw)
                    self.road_lanewidth.append(waypoints[0].lane_width)

                for waypoints in next_waypoints:
                    self.plot_data_road_x.append(waypoints[0].transform.location.x)
                    self.plot_data_road_y.append(waypoints[0].transform.location.y)
                    # self.plot_data_road_psi.append(waypoints[0].transform.rotation.yaw)
                    self.road_lanewidth.append(waypoints[0].lane_width)

                ## CALCULATE HIER DE PSI VAN DE VECTOREN WANT DAT KUT OPENDRIVE FUCKED HET

                pos_array = np.array([[self.plot_data_road_x], [self.plot_data_road_y]])

                diff = np.transpose(np.diff(pos_array, prepend=pos_array))

                x_unit_vector = np.array([[1], [0]])
                for row in diff:
                    self.plot_data_road_psi.append(self.compute_angle(row.ravel(), x_unit_vector.ravel()))

                iter_x = 0
                for roadpoint_x in self.plot_data_road_x:
                    self.plot_data_road_x_outer.append(roadpoint_x - math.sin(self.plot_data_road_psi[iter_x]) * self.road_lanewidth[iter_x] / 2)
                    self.plot_data_road_x_inner.append(roadpoint_x + math.sin(self.plot_data_road_psi[iter_x]) * self.road_lanewidth[iter_x] / 2)
                    iter_x = iter_x + 1

                iter_y = 0
                for roadpoint_y in self.plot_data_road_y:
                    self.plot_data_road_y_outer.append(roadpoint_y - math.cos(self.plot_data_road_psi[iter_y]) * self.road_lanewidth[iter_y] / 2)
                    self.plot_data_road_y_inner.append(roadpoint_y + math.cos(self.plot_data_road_psi[iter_y]) * self.road_lanewidth[iter_y] / 2)
                    iter_y = iter_y + 1

                max_plotrange_x = self.plot_data_road_x[24] + 15
                min_plotrange_x = self.plot_data_road_x[24] - 15
                max_plotrange_y = self.plot_data_road_y[24] + 25
                min_plotrange_y = self.plot_data_road_y[24] - 25

                self.road_outer_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
                self.road_outer_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

                self.road_inner_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
                self.road_inner_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

                self.auto_position_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
                self.auto_position_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

                self.HCR_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
                self.HCR_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

                tr = QtGui.QTransform()
                angle_rot = tr.rotate(vehicle_rotation + (math.degrees(self.plot_data_road_psi[24])))
                rot_carSymbol = angle_rot.map(self.carSymbol)

                self.car_trace_x.append(vehicle_location.x)
                self.car_trace_y.append(vehicle_location.y)
                self.car_trace_psi.append(rot_carSymbol)
                if len(self.car_trace_x) > self.car_trace_length:
                    self.car_trace_x.pop(0)
                    self.car_trace_y.pop(0)
                    self.car_trace_psi.pop(0)

                self.road_outer_plot_handle.setData(x=self.plot_data_road_x_outer[0:-2], y=self.plot_data_road_y_outer[0:-2])
                self.road_inner_plot_handle.setData(x=self.plot_data_road_x_inner[0:-2], y=self.plot_data_road_y_inner[0:-2])
                self.module_dialog.module_widget.top_view_graph.setXRange(min_plotrange_x, max_plotrange_x, padding=0)
                self.module_dialog.module_widget.top_view_graph.setYRange(min_plotrange_y, max_plotrange_y, padding=0)

                self.plot_data_road_x = []
                self.plot_data_road_y = []
                self.plot_data_road_x_outer = []
                self.plot_data_road_x_inner = []
                self.plot_data_road_y_outer = []
                self.plot_data_road_y_inner = []
                self.plot_data_road_psi = []
                self.plot_data_road_psi_deg = []
                self.road_lanewidth = []
                self.converted_y_road_outer = []
                self.converted_x_road_outer = []

            else:
                self.module_dialog.module_widget.top_view_graph.clear()

        self.auto_position_plot_handle.setData(x=self.car_trace_x, y=self.car_trace_y, symbol=self.car_trace_psi, symbolPen=self.car_pens, symbolBrush=self.car_brushes)

        # Big Torque vs steering Angle plot
        self.plot_data_torque_x.append(steering_ang)
        if 'SensoDrive 1' in data_from_hardware_manager.keys():
            self.plot_data_torque_y.append(actual_torque)
        else:
            self.plot_data_torque_y.append(req_torque)
        if len(self.plot_data_torque_x) > self.amount_of_remaining_points:
            self.plot_data_torque_y.pop(0)
            self.plot_data_torque_x.pop(0)
            self.torque_plot_handle.setData(x=self.plot_data_torque_x, y=self.plot_data_torque_y, size=10,
                                            pen=pg.mkPen((169, 169, 169, 120)), brush='g', symbol='d',
                                            symbolBrush=self.brushes, symbolPen=self.pens, symbolSize=10)
            self.sw_des_point_plot_handle.setData(x=[self.plot_data_sw_des_y[-1]], y=[0], symbol='x', symbolSize=15,
                                                  symbolBrush=pg.mkBrush(255, 0, 0, 255),
                                                  symbolPen=pg.mkPen((255, 0, 0, 255), width=3))

        # Steering Wheel stiffness
        self.plot_data_sw_stiffness_y = [sw_stiffness * 160, sw_stiffness * -160]
        self.sw_stiffness_plot_handle.setData(x=self.plot_data_sw_stiffness_x, y=self.plot_data_sw_stiffness_y, size=2,
                                              pen='b',
                                              brush='b', symbol=None,
                                              )
        # ERROR PLOTS
        # Lateral Position Plot
        self.plot_data_e_lat_y.append(lat_error)
        self.plot_data_e_lat_y.pop(0)
        if self.module_dialog.module_widget.check_lat_e.isChecked():
            self.e_lat_plot_handle.setData(x=self.time_list, y=self.plot_data_e_lat_y, size=2,
                                           pen=pg.mkPen((255, 0, 0, 255), width=3),
                                           brush='g', symbol=None)
        else:
            self.e_lat_plot_handle.setData(pen=pg.mkPen((255, 0, 0, 0)))

        if self.module_dialog.module_widget.check_psi_e.isChecked():
            self.plot_data_e_psi_y.append(heading_error)
            self.plot_data_e_psi_y.pop(0)
            self.head_error_plot_handle.setData(x=self.time_list, y=self.plot_data_e_psi_y, size=2,
                                                pen=pg.mkPen((0, 0, 255, 255), width=3),
                                                brush='g', symbol=None)
        else:
            self.head_error_plot_handle.setData(pen=pg.mkPen((0, 0, 255, 0)))

        # TORQUE PLOTS
        # Feedback torque
        if self.module_dialog.module_widget.check_fb.isChecked():
            self.plot_data_fb_torque_y.append(fb_torque)
            self.plot_data_fb_torque_y.pop(0)
            self.fb_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_fb_torque_y, size=2,
                                               pen=pg.mkPen((0, 114, 190, 200), width=3),
                                               brush='g', symbol=None, symbolBrush=self.brushes,
                                               symbolPen=self.pens, symbolSize=5)
        else:
            self.fb_torque_plot_handle.setData(pen=pg.mkPen((0, 114, 190, 0)))

        # Feed forward Torque
        if self.module_dialog.module_widget.check_ff.isChecked():
            self.plot_data_ff_torque_y.append(ff_torque)
            self.plot_data_ff_torque_y.pop(0)
            self.ff_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_ff_torque_y, size=2,
                                               pen=pg.mkPen((217, 83, 25, 200), width=3),
                                               brush='g', symbol=None, symbolBrush=self.brushes,
                                               symbolPen=self.pens, symbolSize=5)
        else:
            self.ff_torque_plot_handle.setData(pen=pg.mkPen((217, 83, 25, 0)))

        # LOHA Torque
        if self.module_dialog.module_widget.check_loha.isChecked():
            self.plot_data_loha_torque_y.append(loha_torque)
            self.plot_data_loha_torque_y.pop(0)
            self.loha_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_loha_torque_y, size=2,
                                                 pen=pg.mkPen((34, 139, 34, 200), width=3),
                                                 brush='g', symbol=None, symbolBrush=self.brushes,
                                                 symbolPen=self.pens, symbolSize=5)
        else:
            self.loha_torque_plot_handle.setData(pen=pg.mkPen((34, 139, 34, 0)))

        if self.module_dialog.module_widget.check_total.isChecked():
            # total Torque
            self.plot_data_total_torque_y.append(loha_torque + ff_torque + fb_torque)
            self.plot_data_total_torque_y.pop(0)
            self.total_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_loha_torque_y, size=2,
                                                  pen=pg.mkPen((0, 0, 0, 200), width=3),
                                                  brush='g', symbol=None, symbolBrush=self.brushes,
                                                  symbolPen=self.pens, symbolSize=5)
        else:
            self.total_torque_plot_handle.setData(pen=pg.mkPen((0, 0, 0, 0)))

        # SW PLOTS
        # sw desired plot
        if self.module_dialog.module_widget.check_sw_des.isChecked():
            self.plot_data_sw_des_y.append(sw_des)
            self.plot_data_sw_des_y.pop(0)
            self.sw_des_plot_handle.setData(x=self.time_list, y=self.plot_data_sw_des_y, size=2,
                                            pen=pg.mkPen((0, 114, 190, 200), width=3), brush=pg.mkBrush((0, 114, 190, 200)),
                                            symbol=None,
                                            symbolBrush=pg.mkBrush((0, 114, 190, 200)),
                                            symbolPen=pg.mkPen((0, 114, 190, 200)), symbolSize=3)
        else:
            self.sw_des_plot_handle.setData(pen=pg.mkPen((0, 114, 190, 0)))

        # sw actual plot
        if self.module_dialog.module_widget.check_sw_act.isChecked():
            self.plot_data_sw_act_y.append(sw_actual)
            self.plot_data_sw_act_y.pop(0)
            self.sw_act_plot_handle.setData(x=self.time_list, y=self.plot_data_sw_act_y, size=5,
                                            pen=pg.mkPen((217, 83, 25, 200), width=3), brush=pg.mkBrush((217, 83, 25, 200)),
                                            symbol=None, symbolBrush=pg.mkBrush((217, 83, 25, 200)),
                                            symbolPen=pg.mkPen((217, 83, 25, 200)), symbolSize=3)
        else:
            self.sw_act_plot_handle.setData(pen=pg.mkPen((217, 83, 25, 0)))

    def compute_angle(self, v1, v2):
        arg1 = np.cross(v1, v2)
        arg2 = np.dot(v1, v2)
        angle = np.arctan2(arg1, arg2)
        return angle

    def initialize(self):
        """
        This function is called before the module is started
        """

        # Top view graph
        # TODO: Make this depend on the trajectory selected in FDCA controller (read news and then apply that name)
        trajectory_name = "MiddleRoadTVRecord_filtered_ffswang_heading_2hz.csv"
        tmp = pd.read_csv(os.path.join('modules/steeringwheelcontrol/action/swcontrollers/trajectories', trajectory_name))
        HCR_trajectory_data = tmp.values
        plot_data_HCR_x = HCR_trajectory_data[:, 1]
        plot_data_HCR_y = HCR_trajectory_data[:, 2]

        self.carSymbol = QtGui.QPainterPath()
        self.carSymbol.addRect(-0.2, -0.4, 0.4, 0.8)

        self.HCR_plot_handle = self.module_dialog.module_widget.top_view_graph.plot(x=plot_data_HCR_x, y=plot_data_HCR_y, pen=pg.mkPen(10, 200, 0, 100, width=18))

        self.auto_position_plot_handle = self.module_dialog.module_widget.top_view_graph.plot(x=[0], y=[0], symbol=self.carSymbol,
                                                                                              symbolSize=40, pen=None,
                                                                                              symbolBrush=pg.mkBrush(200,
                                                                                                                     0,
                                                                                                                     0,
                                                                                                                     255),
                                                                                              symbolPen=pg.mkPen(
                                                                                                  (200, 0, 0, 255),
                                                                                                  width=3))
        self.road_plot_handle = self.module_dialog.module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
                                                                                     pen=pg.mkPen((0, 0, 0, 200),
                                                                                                  width=1),
                                                                                     brush='g', symbol=None,
                                                                                     symbolBrush=self.brushes,
                                                                                     symbolPen=self.pens, symbolSize=5)
        self.road_outer_plot_handle = self.module_dialog.module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
                                                                                           pen=pg.mkPen((0, 0, 0, 255),
                                                                                                        width=2),
                                                                                           brush='g', symbol=None,
                                                                                           symbolBrush=self.brushes,
                                                                                           symbolPen=self.pens, symbolSize=5)

        self.road_inner_plot_handle = self.module_dialog.module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
                                                                                           pen=pg.mkPen((0, 0, 0, 255),
                                                                                                        width=2),
                                                                                           brush='g', symbol=None,
                                                                                           symbolBrush=self.brushes,
                                                                                           symbolPen=self.pens, symbolSize=5)
        # big torque graph

        self.sw_des_point_plot_handle = self.module_dialog.module_widget.torque_graph.plot(x=[0], y=[0], symbol='x',
                                                                                           symbolSize=15, pen=None,
                                                                                           symbolBrush=pg.mkBrush(255,
                                                                                                                  0,
                                                                                                                  0,
                                                                                                                  255),
                                                                                           symbolPen=pg.mkPen(
                                                                                               (255, 0, 0, 255),
                                                                                               width=3))
        self.torque_plot_handle = self.module_dialog.module_widget.torque_graph.plot(x=[0], y=[0], size=10,
                                                                                     pen=pg.mkPen((169, 169, 169, 120)),
                                                                                     brush='g', symbol='d',
                                                                                     symbolBrush=self.brushes[-1],
                                                                                     symbolPen=self.pens[-1],
                                                                                     symbolSize=10)
        self.sw_stiffness_plot_handle = self.module_dialog.module_widget.torque_graph.plot(x=[-160, 160], y=[0, 0],
                                                                                           pen='b',
                                                                                           brush='b', symbol=None,
                                                                                           )
        # error graphs
        # lat pos graph
        self.e_lat_plot_handle = self.module_dialog.module_widget.errors_graph.plot(x=[0], y=[0], size=2,
                                                                                    pen=pg.mkPen((255, 0, 0, 255),
                                                                                                 width=3),
                                                                                    brush='g', symbol=None,
                                                                                    symbolBrush=self.brushes,
                                                                                    symbolPen=self.pens, symbolSize=5)

        # Heading error graph
        self.head_error_plot_handle = self.module_dialog.module_widget.errors_graph.plot(x=[0], y=[0], size=2,
                                                                                         pen=pg.mkPen((0, 0, 255, 255),
                                                                                                      width=3),
                                                                                         brush='g', symbol=None,
                                                                                         symbolBrush=self.brushes,
                                                                                         symbolPen=self.pens, symbolSize=5)
        # Feedback torques graph

        self.fb_torque_plot_handle = self.module_dialog.module_widget.fb_torques_graph.plot(x=[0], y=[0], size=2,
                                                                                            pen=pg.mkPen(
                                                                                                (0, 114, 190, 200),
                                                                                                width=3),
                                                                                            brush='g', symbol=None,
                                                                                            symbolBrush=self.brushes,
                                                                                            symbolPen=self.pens,
                                                                                            symbolSize=5)
        self.ff_torque_plot_handle = self.module_dialog.module_widget.fb_torques_graph.plot(x=[0], y=[0], size=2,
                                                                                            pen=pg.mkPen(
                                                                                                (217, 83, 25, 200),
                                                                                                width=3),
                                                                                            brush='g', symbol=None,
                                                                                            symbolBrush=self.brushes,
                                                                                            symbolPen=self.pens,
                                                                                            symbolSize=5)
        self.loha_torque_plot_handle = self.module_dialog.module_widget.fb_torques_graph.plot([0], [0], size=2,
                                                                                              pen=pg.mkPen(
                                                                                                  (34, 139, 34),
                                                                                                  width=3),
                                                                                              brush='g', symbol=None,
                                                                                              symbolBrush=self.brushes,
                                                                                              symbolPen=self.pens,
                                                                                              symbolSize=5)
        self.total_torque_plot_handle = self.module_dialog.module_widget.fb_torques_graph.plot([0], [0], size=2,
                                                                                               pen=pg.mkPen(
                                                                                                   (0, 0, 0),
                                                                                                   width=3),
                                                                                               brush='g', symbol=None,
                                                                                               symbolBrush=self.brushes,
                                                                                               symbolPen=self.pens,
                                                                                               symbolSize=5)

        # Steering angle graphs:
        self.sw_des_plot_handle = self.module_dialog.module_widget.sw_graph.plot(x=[0],
                                                                                 y=[0], size=2,
                                                                                 pen=pg.mkPen((0, 114, 190, 200),
                                                                                              width=3),
                                                                                 brush=pg.mkBrush((0, 114, 190, 200)),
                                                                                 symbol=None,
                                                                                 symbolBrush=pg.mkBrush(
                                                                                     (0, 114, 190, 200)),
                                                                                 symbolPen=pg.mkPen((0, 114, 190, 200)),
                                                                                 symbolSize=3)
        self.sw_act_plot_handle = self.module_dialog.module_widget.sw_graph.plot(x=[0], y=[0], size=5,
                                                                                 pen=pg.mkPen((217, 83, 25, 200),
                                                                                              width=3),
                                                                                 brush=pg.mkBrush((217, 83, 25, 200)),
                                                                                 symbol=None, symbolBrush=pg.mkBrush(
                (217, 83, 25, 200)),
                                                                                 symbolPen=pg.mkPen((217, 83, 25, 200)),
                                                                                 symbolSize=3)

        # self.loha_plot_handle = self.module_dialog.module_widget.loha_graph.plot()

        ## Initialize topview Graph
        self.module_dialog.module_widget.top_view_graph.setXRange(- 15, 15, padding=0)
        self.module_dialog.module_widget.top_view_graph.setYRange(-25, 25, padding=0)
        # self.module_dialog.module_widget.top_view_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.top_view_graph.setTitle('Top View')
        self.module_dialog.module_widget.top_view_graph.setLabel('left', 'Y position [m]',
                                                                 **{'font-size': '10pt'})
        self.module_dialog.module_widget.top_view_graph.setLabel('bottom', '<font>&Theta;X position</font> [m]',
                                                                 **{'font-size': '10pt'})
        top_view_viewbox = self.module_dialog.module_widget.top_view_graph.getViewBox()
        top_view_viewbox.invertX(False)
        top_view_viewbox.invertY(True)
        top_view_viewbox.setBorder(pen=pg.mkPen(0, 0, 0, 255))
        top_view_viewbox.setBackgroundColor((255, 255, 255, 200))
        top_view_legend = pg.LegendItem(offset=None, horSpacing=30, verSpacing=-7,
                                        pen=pg.mkPen(0, 0, 0, 0), brush=pg.mkBrush(255, 255, 255, 255))
        top_view_legend.setParentItem(top_view_viewbox)
        top_view_legend.addItem(self.HCR_plot_handle, name='HCR')

        ## Initialize Torque Graph
        self.module_dialog.module_widget.torque_graph.setXRange(- 180, 180, padding=0)
        self.module_dialog.module_widget.torque_graph.setYRange(-7.5, 7.5, padding=0)
        self.module_dialog.module_widget.torque_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.torque_graph.setTitle('Steering Angle vs Torque')
        self.module_dialog.module_widget.torque_graph.setLabel('left', 'Torque [Nm]',
                                                               **{'font-size': '10pt'})
        self.module_dialog.module_widget.torque_graph.setLabel('bottom', '<font>&Theta;Steering Wheel</font> [deg]',
                                                               **{'font-size': '10pt'})
        self.module_dialog.module_widget.torque_graph.getAxis('bottom').setTickFont(self.labelfont)
        self.module_dialog.module_widget.torque_graph.getAxis("bottom").setStyle(tickTextOffset=10)
        self.module_dialog.module_widget.torque_graph.getAxis('left').setTickFont(self.labelfont)
        self.module_dialog.module_widget.torque_graph.getAxis("left").setStyle(tickTextOffset=10)
        torque_viewbox = self.module_dialog.module_widget.torque_graph.getViewBox()
        torque_viewbox.invertX(False)
        torque_viewbox.invertY(True)
        torque_viewbox.setBackgroundColor((255, 255, 255, 200))
        torque_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
                                      pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        torque_legend.setParentItem(torque_viewbox)
        torque_legend.addItem(self.torque_plot_handle, name='Torque vs Steering Angle')
        torque_legend.addItem(self.sw_des_point_plot_handle, name='Desired Steering Angle')
        torque_legend.addItem(self.sw_stiffness_plot_handle, name='Self Centering Stiffness')

        ## Initialize Errors Plot
        self.module_dialog.module_widget.errors_graph.setTitle('Lateral position vs Time')
        self.module_dialog.module_widget.errors_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.errors_graph.setYRange(-8, 8, padding=0)
        self.module_dialog.module_widget.errors_graph.setLabel('right', 'Lat Pos [m]', **{'font-size': '12pt'})
        self.module_dialog.module_widget.errors_graph.setLabel('left', 'Heading Error [deg]', **{'font-size': '12pt'})
        errors_viewbox = self.module_dialog.module_widget.errors_graph.getViewBox()
        errors_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
                                      pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        errors_legend.setParentItem(errors_viewbox)
        errors_legend.addItem(self.e_lat_plot_handle, name='Lateral position Error')

        # viewbox 2 for double axis
        p2 = pg.ViewBox()
        p2.setYRange(-90, 90)
        p2.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.errors_graph.showGrid(True, True, 0.5)
        self.module_dialog.module_widget.errors_graph.showAxis('right')
        self.module_dialog.module_widget.errors_graph.scene().addItem(p2)
        self.module_dialog.module_widget.errors_graph.getAxis('left').linkToView(p2)
        p2.setXLink(self.module_dialog.module_widget.errors_graph)
        p2.addItem(self.head_error_plot_handle)
        p2.setBackgroundColor((255, 255, 255, 200))
        self.module_dialog.module_widget.errors_graph.getAxis('left').setPen(pg.mkPen(0, 0, 255, 255))
        self.module_dialog.module_widget.errors_graph.getAxis('right').setPen(pg.mkPen(255, 0, 0, 255))

        ## Handle view resizing
        def updateViews():
            ## view has resized; update auxiliary views to match
            p2.setGeometry(errors_viewbox.sceneBoundingRect())
            p2.linkedViewChanged(errors_viewbox, p2.XAxis)

        updateViews()
        errors_viewbox.sigResized.connect(updateViews)
        errors_legend.addItem(self.head_error_plot_handle, name='Heading Error')

        ## Initialize fb torque Plot
        self.module_dialog.module_widget.fb_torques_graph.setTitle('Feedback Torques vs Time')
        self.module_dialog.module_widget.fb_torques_graph.setXRange(-self.history_time, self.history_time / 10,
                                                                    padding=0)
        self.module_dialog.module_widget.fb_torques_graph.setYRange(-10, 10, padding=0)
        self.module_dialog.module_widget.fb_torques_graph.setLabel('right', 'Torques [Nm]',
                                                                   **{'font-size': '12pt'})
        torques_viewbox = self.module_dialog.module_widget.fb_torques_graph.getViewBox()
        torques_viewbox.setBackgroundColor((255, 255, 255, 200))
        torques_viewbox.invertY(True)
        torques_legend = pg.LegendItem(size=(120, 60), offset=None, horSpacing=30, verSpacing=-7,
                                       pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        torques_legend.setParentItem(torques_viewbox)
        torques_legend.addItem(self.fb_torque_plot_handle, name='Feedback Torque')
        torques_legend.addItem(self.ff_torque_plot_handle, name='Feedforward Torque')
        torques_legend.addItem(self.loha_torque_plot_handle, name='LoHA Torque')
        torques_legend.addItem(self.total_torque_plot_handle, name='Total Torque')
        self.module_dialog.module_widget.fb_torques_graph.showGrid(True, True, 1)

        ## Initialize sw angle Plot
        self.module_dialog.module_widget.sw_graph.setTitle('Steering Angles vs Time')
        self.module_dialog.module_widget.sw_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self.module_dialog.module_widget.sw_graph.setYRange(-185, 185, padding=0)
        self.module_dialog.module_widget.sw_graph.showGrid(True, True, 1)
        self.module_dialog.module_widget.sw_graph.setLabel('right', '<font>&Theta;SW</font>[deg]',
                                                           **{'font-size': '12pt'})
        self.module_dialog.module_widget.sw_graph.setLabel('bottom', 'Time[s]', **{'font-size': '12pt'})
        sw_des_viewbox = self.module_dialog.module_widget.sw_graph.getViewBox()
        sw_des_viewbox.setBackgroundColor((255, 255, 255, 200))
        sw_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
                                  pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        sw_legend.setParentItem(sw_des_viewbox)
        sw_legend.addItem(self.sw_des_plot_handle, name='Desired Steering Angle')
        sw_legend.addItem(self.sw_act_plot_handle, name='Actual Steering Angle')

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
        self.module_dialog.module_widget.top_view_graph.clear()
        self.module_dialog.module_widget.torque_graph.clear()
        self.module_dialog.module_widget.errors_graph.clear()
        self.module_dialog.module_widget.fb_torques_graph.clear()
        # self.module_dialog.module_widget.loha_graph.clear()
        self.module_dialog.module_widget.sw_graph.clear()
        # self.module_dialog.module_widget.sw_actual_graph.clear()

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
