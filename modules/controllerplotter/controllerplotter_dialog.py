import math
import os

import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
from colour import Color

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class ControllerPlotterDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        """

        :param module_manager:
        :param parent:
        """
        super().__init__(module=JOANModules.CONTROLLER_PLOTTER, module_manager=module_manager, parent=parent)

        background_color = pg.mkColor((240, 240, 240, 255))

        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'k')

        self._module_widget.top_view_graph.setBackground(background_color)
        self._module_widget.sw_graph.setBackground(background_color)
        self._module_widget.errors_graph.setBackground(background_color)
        self._module_widget.torque_graph.setBackground(background_color)
        self._module_widget.fb_torques_graph.setBackground(background_color)

        # initialize lists and variables for plotting
        self.amount_of_remaining_points = 50
        self.car_trace_length = 10

        # dialog will always update at 10hz
        self.history_time = self.amount_of_remaining_points / round(1000 / 100)
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
        self.plot_data_road_x = [0] * 50
        self.plot_data_road_x_outer = [0] * 50
        self.plot_data_road_x_inner = [0] * 50
        self.plot_data_road_y = [0] * 50
        self.plot_data_road_y_outer = [0] * 50
        self.plot_data_road_y_inner = [0] * 50
        self.plot_data_road_psi = [0] * 50
        self.road_lanewidth = [0] * 50
        self.car_trace_x = [0] * self.car_trace_length
        self.car_trace_y = [0] * self.car_trace_length
        self.car_trace_psi = [0] * self.car_trace_length
        self.plot_data_lat_error_topview_x = [0] * 2
        self.plot_data_lat_error_topview_y = [0] * 2
        self.plot_data_car_heading_line_x = [0] * 2
        self.plot_data_car_heading_line_y = [0] * 2
        self.plot_data_HCR_heading_line_x = [0] * 2
        self.plot_data_HCR_heading_line_y = [0] * 2
        self.plot_data_heading_error_top_view_x = [0] * 50
        self.plot_data_heading_error_top_view_y = [0] * 50
        self.plot_data_sw_stiffness_x = [-160, 160]
        self.plot_data_sw_stiffness_y = [0, 0]
        self.plot_data_loha_stiffness_x = [-160, 160]
        self.plot_data_loha_stiffness_shifted = []
        self.plot_data_loha_stiffness_y = [0, 0]
        self.converted_x_road_outer = [] * 50
        self.converted_y_road_outer = [] * 50
        # change labelfont
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
        colors = list(red.range_to(Color("blue"), self.amount_of_remaining_points))
        colors_car = list(red.range_to(Color("blue"), self.car_trace_length))
        for color in colors:
            colors_rgb.append(color.rgb)

        for color_car in colors_car:
            colors_rgb_car.append(color_car.rgb)

        for k in range(self.amount_of_remaining_points):
            self.brushes.append(
                pg.mkBrush(round(200 * colors_rgb[k][0]), round(200 * colors_rgb[k][1]), round(200 * colors_rgb[k][2]),
                           k * 3))
            self.pens.append(
                pg.mkPen(round(200 * colors_rgb[k][0]), round(200 * colors_rgb[k][1]), round(200 * colors_rgb[k][2]),
                         k * 3))

        for k in range(self.car_trace_length):
            self.car_brushes.append(
                pg.mkBrush(round(200 * colors_rgb_car[k][0]), round(200 * colors_rgb_car[k][1]), round(200 * colors_rgb_car[k][2]),
                           k * 25))
            self.car_pens.append(
                pg.mkPen((0, 0, 0,
                          k * 25), width=3))

        self.double_pens = self.pens + self.pens
        self.double_brushes = self.brushes + self.brushes

        self.data = {}

        self.car_symbol = None

    def initialize(self):
        """
        This function is called before the module is started
        """
        haptic_controller_settings = self.module_manager.singleton_settings.get_settings(JOANModules.HAPTIC_CONTROLLER_MANAGER)
        carla_interface_settings = self.module_manager.singleton_settings.get_settings(JOANModules.CARLA_INTERFACE)
        if carla_interface_settings:
            for agent in carla_interface_settings.agents.values():
                if agent.__str__() == 'Ego Vehicle_1':
                    controller = agent.selected_controller
                    if controller != 'None':
                        trajectory_name = haptic_controller_settings.haptic_controllers[controller].trajectory_name
                else:
                    trajectory_name = 'None'

        # Top view graph
        try:
            tmp = pd.read_csv(os.path.join('modules/hapticcontrollermanager/hapticcontrollermanager_controllers/trajectories', trajectory_name))
            HCR_trajectory_data = tmp.values
            plot_data_HCR_x = HCR_trajectory_data[:, 1]
            plot_data_HCR_y = HCR_trajectory_data[:, 2]

            self.HCR_plot_handle = self._module_widget.top_view_graph.plot(x=plot_data_HCR_x, y=plot_data_HCR_y, shadowPen=pg.mkPen(10, 200, 0, 100, width=18),
                                                                           pen=pg.mkPen(0, 102, 0, 255, width=2))
        except:
            print('Could not find HCR trajectory, please hardcode a name that is in your sw controller trajectory list ')
            self.HCR_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], shadowPen=pg.mkPen(10, 200, 0, 100, width=18),
                                                                           pen=pg.mkPen(0, 102, 0, 255, width=2))
        self.car_symbol = QtGui.QPainterPath()
        self.car_symbol.addRect(-0.2, -0.4, 0.4, 0.8)

        self.auto_position_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], symbol=self.car_symbol,
                                                                                 symbolSize=40, pen=None,
                                                                                 symbolBrush=pg.mkBrush(0,
                                                                                                        0,
                                                                                                        255,
                                                                                                        255),
                                                                                 symbolPen=pg.mkPen(
                                                                                     (0, 0, 0, 255),
                                                                                     width=2))
        self.road_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
                                                                        pen=pg.mkPen((0, 0, 0, 200),
                                                                                     width=1, style=QtCore.Qt.DashLine),
                                                                        brush='g', symbol=None,
                                                                        symbolBrush=self.brushes,
                                                                        symbolPen=self.pens, symbolSize=5)
        self.road_outer_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
                                                                              pen=pg.mkPen((0, 0, 0, 255),
                                                                                           width=2),
                                                                              brush='g', symbol=None,
                                                                              symbolBrush=self.brushes,
                                                                              symbolPen=self.pens, symbolSize=5)

        self.road_inner_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
                                                                              pen=pg.mkPen((0, 0, 0, 255),
                                                                                           width=2),
                                                                              brush='g', symbol=None,
                                                                              symbolBrush=self.brushes,
                                                                              symbolPen=self.pens, symbolSize=5)
        self.topview_lat_error_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
                                                                                     pen=pg.mkPen((255, 0, 0, 255),
                                                                                                  width=3))

        self.topview_heading_line_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], pen=pg.mkPen((0, 0, 0, 255),
                                                                                                                   width=1))
        self.topview_HCR_heading_line_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], pen=pg.mkPen((0, 0, 0, 255),
                                                                                                                       width=1))
        self.topview_heading_error_plot_handle = self._module_widget.top_view_graph.plot(x=[0], y=[0], size=2, pen=pg.mkPen((0, 0, 255, 255), width=3))
        # big torque graph

        self.sw_des_point_plot_handle = self._module_widget.torque_graph.plot(x=[0], y=[0], symbol='x',
                                                                              symbolSize=15, pen=None,
                                                                              symbolBrush=pg.mkBrush(255,
                                                                                                     0,
                                                                                                     0,
                                                                                                     255),
                                                                              symbolPen=pg.mkPen(
                                                                                  (255, 0, 0, 255),
                                                                                  width=3))
        self.torque_plot_handle = self._module_widget.torque_graph.plot(x=[0], y=[0], size=10,
                                                                        pen=pg.mkPen((169, 169, 169, 120)),
                                                                        brush='g', symbol='d',
                                                                        symbolBrush=self.brushes[-1],
                                                                        symbolPen=self.pens[-1],
                                                                        symbolSize=10)
        self.sw_stiffness_plot_handle = self._module_widget.torque_graph.plot(x=[-160, 160], y=[0, 0],
                                                                              pen='b',
                                                                              brush='b', symbol=None,
                                                                              )
        # error graphs
        # lat pos graph
        self.e_lat_plot_handle = self._module_widget.errors_graph.plot(x=[0], y=[0], size=2,
                                                                       pen=pg.mkPen((255, 0, 0, 255),
                                                                                    width=3),
                                                                       brush='g', symbol=None,
                                                                       symbolBrush=self.brushes,
                                                                       symbolPen=self.pens, symbolSize=5)

        # Heading error graph
        self.head_error_plot_handle = self._module_widget.errors_graph.plot(x=[0], y=[0], size=2,
                                                                            pen=pg.mkPen((0, 0, 255, 255),
                                                                                         width=3),
                                                                            brush='g', symbol=None,
                                                                            symbolBrush=self.brushes,
                                                                            symbolPen=self.pens, symbolSize=5)
        # Feedback torques graph
        self.fb_torque_plot_handle = self._module_widget.fb_torques_graph.plot(x=[0], y=[0], size=2,
                                                                               pen=pg.mkPen(
                                                                                   (0, 114, 190, 200),
                                                                                   width=3),
                                                                               brush='g', symbol=None,
                                                                               symbolBrush=self.brushes,
                                                                               symbolPen=self.pens,
                                                                               symbolSize=5)
        self.ff_torque_plot_handle = self._module_widget.fb_torques_graph.plot(x=[0], y=[0], size=2,
                                                                               pen=pg.mkPen(
                                                                                   (217, 83, 25, 200),
                                                                                   width=3),
                                                                               brush='g', symbol=None,
                                                                               symbolBrush=self.brushes,
                                                                               symbolPen=self.pens,
                                                                               symbolSize=5)
        self.loha_torque_plot_handle = self._module_widget.fb_torques_graph.plot([0], [0], size=2,
                                                                                 pen=pg.mkPen(
                                                                                     (34, 139, 34),
                                                                                     width=3),
                                                                                 brush='g', symbol=None,
                                                                                 symbolBrush=self.brushes,
                                                                                 symbolPen=self.pens,
                                                                                 symbolSize=5)
        self.total_torque_plot_handle = self._module_widget.fb_torques_graph.plot([0], [0], size=2,
                                                                                  pen=pg.mkPen(
                                                                                      (0, 0, 0),
                                                                                      width=3),
                                                                                  brush='g', symbol=None,
                                                                                  symbolBrush=self.brushes,
                                                                                  symbolPen=self.pens,
                                                                                  symbolSize=5)

        # Steering angle graphs:
        self.sw_des_plot_handle = self._module_widget.sw_graph.plot(x=[0],
                                                                    y=[0], size=2,
                                                                    pen=pg.mkPen((0, 114, 190, 200),
                                                                                 width=3),
                                                                    brush=pg.mkBrush((0, 114, 190, 200)),
                                                                    symbol=None,
                                                                    symbolBrush=pg.mkBrush(
                                                                        (0, 114, 190, 200)),
                                                                    symbolPen=pg.mkPen((0, 114, 190, 200)),
                                                                    symbolSize=3)
        self.sw_act_plot_handle = self._module_widget.sw_graph.plot(x=[0], y=[0], size=5,
                                                                    pen=pg.mkPen((217, 83, 25, 200),
                                                                                 width=3),
                                                                    brush=pg.mkBrush((217, 83, 25, 200)),
                                                                    symbol=None, symbolBrush=pg.mkBrush(
                (217, 83, 25, 200)),
                                                                    symbolPen=pg.mkPen((217, 83, 25, 200)),
                                                                    symbolSize=3)

        self.loha_stiffness_plot_handle = self._module_widget.torque_graph.plot(x=[-160, 160], y=[0, 0],
                                                                                pen='m',
                                                                                brush='g', symbol=None,
                                                                                )

        # Initialize topview Graph
        self._module_widget.top_view_graph.setXRange(- 15, 15, padding=0)
        self._module_widget.top_view_graph.setYRange(-25, 25, padding=0)
        self._module_widget.top_view_graph.setTitle('Top View')
        self._module_widget.top_view_graph.setLabel('left', 'Y position [m]',
                                                    **{'font-size': '10pt'})
        self._module_widget.top_view_graph.setLabel('bottom', '<font>X position</font> [m]',
                                                    **{'font-size': '10pt'})
        top_view_viewbox = self._module_widget.top_view_graph.getViewBox()
        top_view_viewbox.invertX(False)
        top_view_viewbox.invertY(True)
        top_view_viewbox.setBorder(pen=pg.mkPen(0, 0, 0, 255))
        top_view_viewbox.setBackgroundColor((255, 255, 255, 200))
        self.top_view_legend = pg.LegendItem(offset=(10, -10), horSpacing=30, verSpacing=2,
                                             pen=pg.mkPen(0, 0, 0, 0), brush=pg.mkBrush(255, 255, 255, 0))
        self.top_view_legend.setParentItem(top_view_viewbox)
        self.top_view_legend.addItem(self.HCR_plot_handle, name='HCR')
        self.top_view_legend.addItem(self.road_outer_plot_handle, name='Lane/Road Edge')
        self.top_view_legend.addItem(self.road_plot_handle, name='Lane/Road Center')
        self.top_view_legend.addItem(self.topview_lat_error_plot_handle, name='Lateral Error')
        self.top_view_legend.addItem(self.topview_heading_error_plot_handle, name='Heading Error')

        # Initialize Torque Graph
        self._module_widget.torque_graph.setXRange(- 180, 180, padding=0)
        self._module_widget.torque_graph.setYRange(-7.5, 7.5, padding=0)
        self._module_widget.torque_graph.showGrid(True, True, 1)
        self._module_widget.torque_graph.setTitle('Steering Angle vs Torque')
        self._module_widget.torque_graph.setLabel('left', 'Torque [Nm]',
                                                  **{'font-size': '10pt'})
        self._module_widget.torque_graph.setLabel('bottom', '<font>&Theta;Steering Wheel</font> [deg]',
                                                  **{'font-size': '10pt'})
        self._module_widget.torque_graph.getAxis('bottom').setTickFont(self.labelfont)
        self._module_widget.torque_graph.getAxis("bottom").setStyle(tickTextOffset=10)
        self._module_widget.torque_graph.getAxis('left').setTickFont(self.labelfont)
        self._module_widget.torque_graph.getAxis("left").setStyle(tickTextOffset=10)
        torque_viewbox = self._module_widget.torque_graph.getViewBox()
        torque_viewbox.invertX(False)
        torque_viewbox.invertY(True)
        torque_viewbox.setBackgroundColor((255, 255, 255, 200))
        self.torque_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
                                           pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        self.torque_legend.setParentItem(torque_viewbox)
        self.torque_legend.addItem(self.torque_plot_handle, name='Torque vs Steering Angle')
        self.torque_legend.addItem(self.sw_des_point_plot_handle, name='Desired Steering Angle')
        self.torque_legend.addItem(self.sw_stiffness_plot_handle, name='Self Centering Stiffness')
        self.torque_legend.addItem(self.loha_stiffness_plot_handle, name='LoHA Stiffness')

        # Initialize Errors Plot
        self._module_widget.errors_graph.setTitle('Lateral position vs Time')
        self._module_widget.errors_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self._module_widget.errors_graph.setYRange(-10, 10, padding=0)
        self._module_widget.errors_graph.setLabel('left', 'Lat Pos [m]', **{'font-size': '12pt'})
        self._module_widget.errors_graph.setLabel('right', 'Heading Error [deg]', **{'font-size': '12pt'})
        errors_viewbox = self._module_widget.errors_graph.getViewBox()
        self.errors_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
                                           pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        self.errors_legend.setParentItem(errors_viewbox)
        self.errors_legend.addItem(self.e_lat_plot_handle, name='Lateral position Error')

        # viewbox 2 for double axis
        p2 = pg.ViewBox()
        p2.setYRange(-99, 99)
        p2.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self._module_widget.errors_graph.showGrid(True, True, 0.5)
        self._module_widget.errors_graph.showAxis('left')
        self._module_widget.errors_graph.scene().addItem(p2)
        self._module_widget.errors_graph.getAxis('right').linkToView(p2)
        self._module_widget.errors_graph.getAxis('left').setGrid(0)
        p2.setXLink(self._module_widget.errors_graph)
        p2.addItem(self.head_error_plot_handle)
        p2.setBackgroundColor((255, 255, 255, 200))
        self._module_widget.errors_graph.getAxis('left').setPen(pg.mkPen(255, 0, 0, 255))
        self._module_widget.errors_graph.getAxis('right').setPen(pg.mkPen(0, 0, 255, 255))

        # Handle view resizing
        def updateViews():
            # view has resized; update auxiliary views to match
            p2.setGeometry(errors_viewbox.sceneBoundingRect())
            p2.linkedViewChanged(errors_viewbox, p2.XAxis)

        updateViews()
        errors_viewbox.sigResized.connect(updateViews)
        self.errors_legend.addItem(self.head_error_plot_handle, name='Heading Error')

        # Initialize fb torque Plot
        self._module_widget.fb_torques_graph.setTitle('Feedback Torques vs Time')
        self._module_widget.fb_torques_graph.setXRange(-self.history_time, self.history_time / 10,
                                                       padding=0)
        self._module_widget.fb_torques_graph.setYRange(-10, 10, padding=0)
        self._module_widget.fb_torques_graph.setLabel('right', 'Torques [Nm]',
                                                      **{'font-size': '12pt'})
        torques_viewbox = self._module_widget.fb_torques_graph.getViewBox()
        torques_viewbox.setBackgroundColor((255, 255, 255, 200))
        torques_viewbox.invertY(True)
        self.torques_legend = pg.LegendItem(size=(120, 60), offset=None, horSpacing=30, verSpacing=-7,
                                            pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        self.torques_legend.setParentItem(torques_viewbox)
        self.torques_legend.addItem(self.fb_torque_plot_handle, name='Feedback Torque')
        self.torques_legend.addItem(self.ff_torque_plot_handle, name='Feedforward Torque')
        self.torques_legend.addItem(self.loha_torque_plot_handle, name='LoHA Torque')
        self.torques_legend.addItem(self.total_torque_plot_handle, name='Total Torque')
        self._module_widget.fb_torques_graph.showGrid(True, True, 1)

        ## Initialize sw angle Plot
        self._module_widget.sw_graph.setTitle('Steering Angles vs Time')
        self._module_widget.sw_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        self._module_widget.sw_graph.setYRange(-185, 185, padding=0)
        self._module_widget.sw_graph.showGrid(True, True, 1)
        self._module_widget.sw_graph.setLabel('right', '<font>&Theta;SW</font>[deg]',
                                              **{'font-size': '12pt'})
        self._module_widget.sw_graph.setLabel('bottom', 'Time[s]', **{'font-size': '12pt'})
        sw_des_viewbox = self._module_widget.sw_graph.getViewBox()
        sw_des_viewbox.setBackgroundColor((255, 255, 255, 200))
        self.sw_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
                                       pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        self.sw_legend.setParentItem(sw_des_viewbox)
        self.sw_legend.addItem(self.sw_des_plot_handle, name='Desired Steering Angle')
        self.sw_legend.addItem(self.sw_act_plot_handle, name='Actual Steering Angle')

    def update_dialog(self):
        "update de hele zooi hier"
        for keys in self.module_manager.singleton_settings.all_settings_keys:
            self.data[keys] = self.module_manager.news.read_news(keys)

        self.do()

    def do(self):
        """
        This function is called every module dialog update tick of this module implement your main calculations here
        """
        try:
            data_from_haptic_controller_manager = self.data[JOANModules.HAPTIC_CONTROLLER_MANAGER].haptic_controllers['FDCA_1']
            data_from_hardware_manager = self.data[JOANModules.HARDWARE_MANAGER].inputs['SensoDrive_1']
            data_from_carla_interface = self.data[JOANModules.CARLA_INTERFACE].agents['Ego Vehicle_1']
        except KeyError:
            data_from_haptic_controller_manager = {}
            data_from_hardware_manager = {}
            data_from_carla_interface = {}

        try:
            steering_ang = math.degrees(data_from_hardware_manager.steering_angle)
            sw_actual = math.degrees(data_from_hardware_manager.steering_angle)
            sw_stiffness = math.radians(data_from_hardware_manager.auto_center_stiffness)
        except AttributeError:
            steering_ang = 0
            sw_actual = 0
            sw_stiffness = math.radians(1)

        # from steeringwheel controller
        try:
            lat_error = data_from_haptic_controller_manager.lat_error
            sw_des = math.degrees(data_from_haptic_controller_manager.sw_des)
            heading_error = math.degrees(data_from_haptic_controller_manager.heading_error)
            ff_torque = data_from_haptic_controller_manager.ff_torque
            fb_torque = data_from_haptic_controller_manager.fb_torque
            loha_torque = data_from_haptic_controller_manager.loha_torque
            req_torque = data_from_haptic_controller_manager.req_torque
            loha = data_from_haptic_controller_manager.loha

        except AttributeError:
            lat_error = 0
            sw_des = 0
            heading_error = 0
            req_torque = 0
            fb_torque = 0
            ff_torque = 0
            loha_torque = 0
            loha = 0

        try:
            actual_torque = data_from_hardware_manager.measured_torque
        except AttributeError:
            actual_torque = req_torque

        # from carla interface
        try:
            car_transform = data_from_carla_interface.transform
            vehicle_rotation = car_transform[3]
            vehicle_location_x = car_transform[0]
            vehicle_location_y = car_transform[1]
            self.plot_data_road_x = data_from_carla_interface.data_road_x
            self.plot_data_road_x_inner = data_from_carla_interface.data_road_x_inner
            self.plot_data_road_x_outer = data_from_carla_interface.data_road_x_outer
            self.plot_data_road_y = data_from_carla_interface.data_road_y
            self.plot_data_road_y_inner = data_from_carla_interface.data_road_y_inner
            self.plot_data_road_y_outer = data_from_carla_interface.data_road_y_outer
            self.plot_data_road_psi = data_from_carla_interface.data_road_psi
            self.plot_data_road_lanewidth = data_from_carla_interface.data_road_lanewidth

        except:
            vehicle_rotation = 0
            vehicle_location_x = 0
            vehicle_location_y = 0
            self.plot_data_road_x = [0] * 50
            self.plot_data_road_x_outer = [0] * 50
            self.plot_data_road_x_inner = [0] * 50
            self.plot_data_road_y = [0] * 50
            self.plot_data_road_y_outer = [0] * 50
            self.plot_data_road_y_inner = [0] * 50
            self.plot_data_road_psi = [0] * 50
            self.road_lanewidth = [0] * 50

        try:

            # Set plotranges (KEEP IT SQUARE)
            max_plotrange_x = self.plot_data_road_x[24] + 20
            min_plotrange_x = self.plot_data_road_x[24] - 20
            max_plotrange_y = self.plot_data_road_y[24] + 20
            min_plotrange_y = self.plot_data_road_y[24] - 20

            # Rotate plots according to the road orientation (makes sure we keep driving 'upwards')
            self.road_outer_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.road_outer_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.road_inner_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.road_inner_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.road_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.road_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.auto_position_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.auto_position_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.topview_lat_error_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.topview_lat_error_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.topview_heading_error_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.topview_heading_error_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.topview_heading_line_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.topview_heading_line_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.topview_HCR_heading_line_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.topview_HCR_heading_line_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            self.HCR_plot_handle.setTransformOriginPoint(self.plot_data_road_x[24], self.plot_data_road_y[24])
            self.HCR_plot_handle.setRotation(math.degrees(self.plot_data_road_psi[24] - 0.5 * math.pi))

            tr = QtGui.QTransform()
            angle_rot = tr.rotate(vehicle_rotation + (math.degrees(self.plot_data_road_psi[24])))
            rot_CarSymbol = angle_rot.map(self.car_symbol)

            self.car_trace_x.append(vehicle_location_x)
            self.car_trace_y.append(vehicle_location_y)
            self.car_trace_psi.append(rot_CarSymbol)

            self.plot_data_lat_error_topview_x = [vehicle_location_x, vehicle_location_x + math.sin(self.plot_data_road_psi[24]) * lat_error]
            self.plot_data_lat_error_topview_y = [vehicle_location_y, vehicle_location_y + math.cos(self.plot_data_road_psi[24]) * lat_error]

            length = 50
            upper = vehicle_rotation + heading_error
            lower = vehicle_rotation
            angles = [lower + x * (upper - lower) / length for x in range(length)]

            for angle in angles:
                self.plot_data_heading_error_top_view_x.append(vehicle_location_x + math.cos(math.radians(angle)) * 10)
                self.plot_data_heading_error_top_view_y.append(vehicle_location_y + math.sin(math.radians(angle)) * 10)

            self.plot_data_car_heading_line_x = [vehicle_location_x, vehicle_location_x + math.cos(math.radians(vehicle_rotation)) * 18]
            self.plot_data_car_heading_line_y = [vehicle_location_y, vehicle_location_y + math.sin(math.radians(vehicle_rotation)) * 18]

            self.plot_data_HCR_heading_line_x = [vehicle_location_x, vehicle_location_x + math.cos(math.radians(vehicle_rotation + heading_error)) * 18]
            self.plot_data_HCR_heading_line_y = [vehicle_location_y, vehicle_location_y + math.sin(math.radians(vehicle_rotation + heading_error)) * 18]

            if len(self.car_trace_x) > self.car_trace_length:
                self.car_trace_x.pop(0)
                self.car_trace_y.pop(0)
                self.car_trace_psi.pop(0)
            self.road_outer_plot_handle.setData(x=self.plot_data_road_x_outer[0:-2], y=self.plot_data_road_y_outer[0:-2])
            self.road_inner_plot_handle.setData(x=self.plot_data_road_x_inner[0:-2], y=self.plot_data_road_y_inner[0:-2])
            self.road_plot_handle.setData(x=self.plot_data_road_x[0:-2], y=self.plot_data_road_y[0:-2])
            self.topview_heading_error_plot_handle.setData(x=self.plot_data_heading_error_top_view_x, y=self.plot_data_heading_error_top_view_y)
            self._module_widget.top_view_graph.setXRange(min_plotrange_x, max_plotrange_x, padding=0)
            self._module_widget.top_view_graph.setYRange(min_plotrange_y, max_plotrange_y, padding=0)

            # Clear lists so we can append them again for the next loop
            self.plot_data_road_x = []
            self.plot_data_road_y = []
            self.plot_data_heading_error_top_view_x = []
            self.plot_data_heading_error_top_view_y = []
            self.plot_data_road_x_outer = []
            self.plot_data_road_x_inner = []
            self.plot_data_road_y_outer = []
            self.plot_data_road_y_inner = []
            self.plot_data_road_psi = []
            self.road_lanewidth = []
            self.converted_y_road_outer = []
            self.converted_x_road_outer = []

            # set data
            self.auto_position_plot_handle.setData(x=self.car_trace_x, y=self.car_trace_y, symbol=self.car_trace_psi, symbolPen=self.car_pens,
                                                   symbolBrush=self.car_brushes)
            self.topview_lat_error_plot_handle.setData(x=self.plot_data_lat_error_topview_x, y=self.plot_data_lat_error_topview_y)
            self.topview_heading_line_plot_handle.setData(x=self.plot_data_car_heading_line_x, y=self.plot_data_car_heading_line_y)
            self.topview_HCR_heading_line_plot_handle.setData(x=self.plot_data_HCR_heading_line_x, y=self.plot_data_HCR_heading_line_y)

            # Big Torque vs steering Angle plot
            self.plot_data_torque_x.append(steering_ang)
            self.plot_data_torque_y.append(actual_torque)
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

            # LoHA Stiffness
            # Steering Wheel stiffness
            self.plot_data_loha_stiffness_y = [math.radians(loha) * 160, math.radians(loha) * -160]
            self.plot_data_loha_stiffness_shifted = [x + self.plot_data_sw_des_y[-1] for x in self.plot_data_loha_stiffness_x]
            self.loha_stiffness_plot_handle.setData(x=self.plot_data_loha_stiffness_shifted, y=self.plot_data_loha_stiffness_y, size=2,
                                                    pen='m',
                                                    brush='m', symbol=None,
                                                    )
            # ERROR PLOTS
            # Lateral Position Plot
            self.plot_data_e_lat_y.append(lat_error)
            self.plot_data_e_lat_y.pop(0)
            if self._module_widget.check_lat_e.isChecked():
                self.e_lat_plot_handle.setData(x=self.time_list, y=self.plot_data_e_lat_y, size=2,
                                               pen=pg.mkPen((255, 0, 0, 255), width=3),
                                               brush='g', symbol=None)
            else:
                self.e_lat_plot_handle.setData(pen=pg.mkPen((255, 0, 0, 0)))

            if self._module_widget.check_psi_e.isChecked():
                self.plot_data_e_psi_y.append(heading_error)
                self.plot_data_e_psi_y.pop(0)
                self.head_error_plot_handle.setData(x=self.time_list, y=self.plot_data_e_psi_y, size=2,
                                                    pen=pg.mkPen((0, 0, 255, 255), width=3),
                                                    brush='g', symbol=None)
            else:
                self.head_error_plot_handle.setData(pen=pg.mkPen((0, 0, 255, 0)))

            # TORQUE PLOTS
            # Feedback torque
            if self._module_widget.check_fb.isChecked():
                self.plot_data_fb_torque_y.append(fb_torque)
                self.plot_data_fb_torque_y.pop(0)
                self.fb_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_fb_torque_y, size=2,
                                                   pen=pg.mkPen((0, 114, 190, 200), width=3),
                                                   brush='g', symbol=None, symbolBrush=self.brushes,
                                                   symbolPen=self.pens, symbolSize=5)
            else:
                self.fb_torque_plot_handle.setData(pen=pg.mkPen((0, 114, 190, 0)))

            # Feed forward Torque
            if self._module_widget.check_ff.isChecked():
                self.plot_data_ff_torque_y.append(ff_torque)
                self.plot_data_ff_torque_y.pop(0)
                self.ff_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_ff_torque_y, size=2,
                                                   pen=pg.mkPen((217, 83, 25, 200), width=3),
                                                   brush='g', symbol=None, symbolBrush=self.brushes,
                                                   symbolPen=self.pens, symbolSize=5)
            else:
                self.ff_torque_plot_handle.setData(pen=pg.mkPen((217, 83, 25, 0)))

            # LOHA Torque
            if self._module_widget.check_loha.isChecked():
                self.plot_data_loha_torque_y.append(loha_torque)
                self.plot_data_loha_torque_y.pop(0)
                self.loha_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_loha_torque_y, size=2,
                                                     pen=pg.mkPen((34, 139, 34, 200), width=3),
                                                     brush='g', symbol=None, symbolBrush=self.brushes,
                                                     symbolPen=self.pens, symbolSize=5)
            else:
                self.loha_torque_plot_handle.setData(pen=pg.mkPen((34, 139, 34, 0)))

            if self._module_widget.check_total.isChecked():
                # total Torque
                self.plot_data_total_torque_y.append(loha_torque + ff_torque + fb_torque)
                self.plot_data_total_torque_y.pop(0)
                self.total_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_total_torque_y, size=2,
                                                      pen=pg.mkPen((0, 0, 0, 200), width=3),
                                                      brush='g', symbol=None, symbolBrush=self.brushes,
                                                      symbolPen=self.pens, symbolSize=5)
            else:
                self.total_torque_plot_handle.setData(pen=pg.mkPen((0, 0, 0, 0)))

            # SW PLOTS
            # sw desired plot
            if self._module_widget.check_sw_des.isChecked():
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
            if self._module_widget.check_sw_act.isChecked():
                self.plot_data_sw_act_y.append(sw_actual)
                self.plot_data_sw_act_y.pop(0)
                self.sw_act_plot_handle.setData(x=self.time_list, y=self.plot_data_sw_act_y, size=5,
                                                pen=pg.mkPen((217, 83, 25, 200), width=3), brush=pg.mkBrush((217, 83, 25, 200)),
                                                symbol=None, symbolBrush=pg.mkBrush((217, 83, 25, 200)),
                                                symbolPen=pg.mkPen((217, 83, 25, 200)), symbolSize=3)
            else:
                self.sw_act_plot_handle.setData(pen=pg.mkPen((217, 83, 25, 0)))

        except:
            pass
