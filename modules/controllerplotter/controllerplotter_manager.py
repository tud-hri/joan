from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
import pandas as pd
import os
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
from colour import Color

class ControllerPlotterManager(ModuleManager):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.CONTROLLER_PLOTTER, time_step_in_ms=time_step_in_ms, parent=parent)
        self.time_step_in_ms = time_step_in_ms



    def initialize(self):
        # """
        # This function is called before the module is started
        # """
        #
        # # Top view graph
        # try:
        #     # TODO: Make this depend on the trajectory selected in FDCA controller (read news and then apply that name)
        #     trajectory_name = "MiddleRoadTVRecord_filtered_ffswang_heading_2hz.csv"
        #     tmp = pd.read_csv(os.path.join('modules/hapticcontrollermanager/hapticcontrollermanager_controllers/trajectories', trajectory_name))
        #     HCR_trajectory_data = tmp.values
        #     plot_data_HCR_x = HCR_trajectory_data[:, 1]
        #     plot_data_HCR_y = HCR_trajectory_data[:, 2]
        #
        #     self.HCR_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=plot_data_HCR_x, y=plot_data_HCR_y, shadowPen=pg.mkPen(10, 200, 0, 100, width=18),
        #                                                                             pen=pg.mkPen(0, 102, 0, 255, width=2))
        # except:
        #     print('Could not find HCR trajectory, please hardcode a name that is in your sw contorller trajectory list ')
        #     self.HCR_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], shadowPen=pg.mkPen(10, 200, 0, 100, width=18),
        #                                                                             pen=pg.mkPen(0, 102, 0, 255, width=2))
        # self.carSymbol = QtGui.QPainterPath()
        # self.carSymbol.addRect(-0.2, -0.4, 0.4, 0.8)
        #
        #
        #
        # self.auto_position_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], symbol=self.carSymbol,
        #                                                                                       symbolSize=40, pen=None,
        #                                                                                       symbolBrush=pg.mkBrush(0,
        #                                                                                                              0,
        #                                                                                                              255,
        #                                                                                                              255),
        #                                                                                       symbolPen=pg.mkPen(
        #                                                                                           (0, 0, 0, 255),
        #                                                                                           width=2))
        # self.road_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
        #                                                                              pen=pg.mkPen((0, 0, 0, 200),
        #                                                                                           width=1, style=QtCore.Qt.DashLine),
        #                                                                              brush='g', symbol=None,
        #                                                                              symbolBrush=self.brushes,
        #                                                                              symbolPen=self.pens, symbolSize=5)
        # self.road_outer_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
        #                                                                                    pen=pg.mkPen((0, 0, 0, 255),
        #                                                                                                 width=2),
        #                                                                                    brush='g', symbol=None,
        #                                                                                    symbolBrush=self.brushes,
        #                                                                                    symbolPen=self.pens, symbolSize=5)
        #
        # self.road_inner_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
        #                                                                                    pen=pg.mkPen((0, 0, 0, 255),
        #                                                                                                 width=2),
        #                                                                                    brush='g', symbol=None,
        #                                                                                    symbolBrush=self.brushes,
        #                                                                                    symbolPen=self.pens, symbolSize=5)
        # self.topview_lat_error_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], size=2,
        #                                                                                           pen=pg.mkPen((255, 0, 0, 255),
        #                                                                                                        width=3))
        #
        # self.topview_heading_line_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], pen=pg.mkPen((0, 0, 0, 255),
        #                                                                                                                         width=1))
        # self.topview_HCR_heading_line_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], pen=pg.mkPen((0, 0, 0, 255),
        #                                                                                                                             width=1))
        # self.topview_heading_error_plot_handle = self.module_dialog._module_widget.top_view_graph.plot(x=[0], y=[0], size=2, pen=pg.mkPen((0, 0, 255, 255), width=3))
        # # big torque graph
        #
        # self.sw_des_point_plot_handle = self.module_dialog._module_widget.torque_graph.plot(x=[0], y=[0], symbol='x',
        #                                                                                    symbolSize=15, pen=None,
        #                                                                                    symbolBrush=pg.mkBrush(255,
        #                                                                                                           0,
        #                                                                                                           0,
        #                                                                                                           255),
        #                                                                                    symbolPen=pg.mkPen(
        #                                                                                        (255, 0, 0, 255),
        #                                                                                        width=3))
        # self.torque_plot_handle = self.module_dialog._module_widget.torque_graph.plot(x=[0], y=[0], size=10,
        #                                                                              pen=pg.mkPen((169, 169, 169, 120)),
        #                                                                              brush='g', symbol='d',
        #                                                                              symbolBrush=self.brushes[-1],
        #                                                                              symbolPen=self.pens[-1],
        #                                                                              symbolSize=10)
        # self.sw_stiffness_plot_handle = self.module_dialog._module_widget.torque_graph.plot(x=[-160, 160], y=[0, 0],
        #                                                                                    pen='b',
        #                                                                                    brush='b', symbol=None,
        #                                                                                    )
        # # error graphs
        # # lat pos graph
        # self.e_lat_plot_handle = self.module_dialog._module_widget.errors_graph.plot(x=[0], y=[0], size=2,
        #                                                                             pen=pg.mkPen((255, 0, 0, 255),
        #                                                                                          width=3),
        #                                                                             brush='g', symbol=None,
        #                                                                             symbolBrush=self.brushes,
        #                                                                             symbolPen=self.pens, symbolSize=5)
        #
        # # Heading error graph
        # self.head_error_plot_handle = self.module_dialog._module_widget.errors_graph.plot(x=[0], y=[0], size=2,
        #                                                                                  pen=pg.mkPen((0, 0, 255, 255),
        #                                                                                               width=3),
        #                                                                                  brush='g', symbol=None,
        #                                                                                  symbolBrush=self.brushes,
        #                                                                                  symbolPen=self.pens, symbolSize=5)
        # # Feedback torques graph
        #
        # self.fb_torque_plot_handle = self.module_dialog._module_widget.fb_torques_graph.plot(x=[0], y=[0], size=2,
        #                                                                                     pen=pg.mkPen(
        #                                                                                         (0, 114, 190, 200),
        #                                                                                         width=3),
        #                                                                                     brush='g', symbol=None,
        #                                                                                     symbolBrush=self.brushes,
        #                                                                                     symbolPen=self.pens,
        #                                                                                     symbolSize=5)
        # self.ff_torque_plot_handle = self.module_dialog._module_widget.fb_torques_graph.plot(x=[0], y=[0], size=2,
        #                                                                                     pen=pg.mkPen(
        #                                                                                         (217, 83, 25, 200),
        #                                                                                         width=3),
        #                                                                                     brush='g', symbol=None,
        #                                                                                     symbolBrush=self.brushes,
        #                                                                                     symbolPen=self.pens,
        #                                                                                     symbolSize=5)
        # self.loha_torque_plot_handle = self.module_dialog._module_widget.fb_torques_graph.plot([0], [0], size=2,
        #                                                                                       pen=pg.mkPen(
        #                                                                                           (34, 139, 34),
        #                                                                                           width=3),
        #                                                                                       brush='g', symbol=None,
        #                                                                                       symbolBrush=self.brushes,
        #                                                                                       symbolPen=self.pens,
        #                                                                                       symbolSize=5)
        # self.total_torque_plot_handle = self.module_dialog._module_widget.fb_torques_graph.plot([0], [0], size=2,
        #                                                                                        pen=pg.mkPen(
        #                                                                                            (0, 0, 0),
        #                                                                                            width=3),
        #                                                                                        brush='g', symbol=None,
        #                                                                                        symbolBrush=self.brushes,
        #                                                                                        symbolPen=self.pens,
        #                                                                                        symbolSize=5)
        #
        # # Steering angle graphs:
        # self.sw_des_plot_handle = self.module_dialog._module_widget.sw_graph.plot(x=[0],
        #                                                                          y=[0], size=2,
        #                                                                          pen=pg.mkPen((0, 114, 190, 200),
        #                                                                                       width=3),
        #                                                                          brush=pg.mkBrush((0, 114, 190, 200)),
        #                                                                          symbol=None,
        #                                                                          symbolBrush=pg.mkBrush(
        #                                                                              (0, 114, 190, 200)),
        #                                                                          symbolPen=pg.mkPen((0, 114, 190, 200)),
        #                                                                          symbolSize=3)
        # self.sw_act_plot_handle = self.module_dialog._module_widget.sw_graph.plot(x=[0], y=[0], size=5,
        #                                                                          pen=pg.mkPen((217, 83, 25, 200),
        #                                                                                       width=3),
        #                                                                          brush=pg.mkBrush((217, 83, 25, 200)),
        #                                                                          symbol=None, symbolBrush=pg.mkBrush(
        #         (217, 83, 25, 200)),
        #                                                                          symbolPen=pg.mkPen((217, 83, 25, 200)),
        #                                                                          symbolSize=3)
        #
        # # self.loha_plot_handle = self.module_dialog._module_widget.loha_graph.plot()
        #
        # ## Initialize topview Graph
        # self.module_dialog._module_widget.top_view_graph.setXRange(- 15, 15, padding=0)
        # self.module_dialog._module_widget.top_view_graph.setYRange(-25, 25, padding=0)
        # self.module_dialog._module_widget.top_view_graph.setTitle('Top View')
        # self.module_dialog._module_widget.top_view_graph.setLabel('left', 'Y position [m]',
        #                                                          **{'font-size': '10pt'})
        # self.module_dialog._module_widget.top_view_graph.setLabel('bottom', '<font>X position</font> [m]',
        #                                                          **{'font-size': '10pt'})
        # top_view_viewbox = self.module_dialog._module_widget.top_view_graph.getViewBox()
        # top_view_viewbox.invertX(False)
        # top_view_viewbox.invertY(True)
        # top_view_viewbox.setBorder(pen=pg.mkPen(0, 0, 0, 255))
        # top_view_viewbox.setBackgroundColor((255, 255, 255, 200))
        # top_view_legend = pg.LegendItem(offset=(10, -10), horSpacing=30, verSpacing=2,
        #                                 pen=pg.mkPen(0, 0, 0, 0), brush=pg.mkBrush(255, 255, 255, 0))
        # top_view_legend.setParentItem(top_view_viewbox)
        # top_view_legend.addItem(self.HCR_plot_handle, name='HCR')
        # top_view_legend.addItem(self.road_outer_plot_handle, name='Lane/Road Edge')
        # top_view_legend.addItem(self.road_plot_handle, name='Lane/Road Center')
        # top_view_legend.addItem(self.topview_lat_error_plot_handle, name='Lateral Error')
        # top_view_legend.addItem(self.topview_heading_error_plot_handle, name='Heading Error')
        #
        # ## Initialize Torque Graph
        # self.module_dialog._module_widget.torque_graph.setXRange(- 180, 180, padding=0)
        # self.module_dialog._module_widget.torque_graph.setYRange(-7.5, 7.5, padding=0)
        # self.module_dialog._module_widget.torque_graph.showGrid(True, True, 1)
        # self.module_dialog._module_widget.torque_graph.setTitle('Steering Angle vs Torque')
        # self.module_dialog._module_widget.torque_graph.setLabel('left', 'Torque [Nm]',
        #                                                        **{'font-size': '10pt'})
        # self.module_dialog._module_widget.torque_graph.setLabel('bottom', '<font>&Theta;Steering Wheel</font> [deg]',
        #                                                        **{'font-size': '10pt'})
        # self.module_dialog._module_widget.torque_graph.getAxis('bottom').setTickFont(self.labelfont)
        # self.module_dialog._module_widget.torque_graph.getAxis("bottom").setStyle(tickTextOffset=10)
        # self.module_dialog._module_widget.torque_graph.getAxis('left').setTickFont(self.labelfont)
        # self.module_dialog._module_widget.torque_graph.getAxis("left").setStyle(tickTextOffset=10)
        # torque_viewbox = self.module_dialog._module_widget.torque_graph.getViewBox()
        # torque_viewbox.invertX(False)
        # torque_viewbox.invertY(True)
        # torque_viewbox.setBackgroundColor((255, 255, 255, 200))
        # torque_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
        #                               pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        # torque_legend.setParentItem(torque_viewbox)
        # torque_legend.addItem(self.torque_plot_handle, name='Torque vs Steering Angle')
        # torque_legend.addItem(self.sw_des_point_plot_handle, name='Desired Steering Angle')
        # torque_legend.addItem(self.sw_stiffness_plot_handle, name='Self Centering Stiffness')
        #
        # ## Initialize Errors Plot
        # self.module_dialog._module_widget.errors_graph.setTitle('Lateral position vs Time')
        # self.module_dialog._module_widget.errors_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        # self.module_dialog._module_widget.errors_graph.setYRange(-10, 10, padding=0)
        # self.module_dialog._module_widget.errors_graph.setLabel('left', 'Lat Pos [m]', **{'font-size': '12pt'})
        # self.module_dialog._module_widget.errors_graph.setLabel('right', 'Heading Error [deg]', **{'font-size': '12pt'})
        # errors_viewbox = self.module_dialog._module_widget.errors_graph.getViewBox()
        # errors_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
        #                               pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        # errors_legend.setParentItem(errors_viewbox)
        # errors_legend.addItem(self.e_lat_plot_handle, name='Lateral position Error')
        #
        # # viewbox 2 for double axis
        # p2 = pg.ViewBox()
        # p2.setYRange(-99, 99)
        # p2.setXRange(-self.history_time, self.history_time / 10, padding=0)
        # self.module_dialog._module_widget.errors_graph.showGrid(True, True, 0.5)
        # self.module_dialog._module_widget.errors_graph.showAxis('left')
        # self.module_dialog._module_widget.errors_graph.scene().addItem(p2)
        # self.module_dialog._module_widget.errors_graph.getAxis('right').linkToView(p2)
        # self.module_dialog._module_widget.errors_graph.getAxis('left').setGrid(0)
        # p2.setXLink(self.module_dialog._module_widget.errors_graph)
        # p2.addItem(self.head_error_plot_handle)
        # p2.setBackgroundColor((255, 255, 255, 200))
        # self.module_dialog._module_widget.errors_graph.getAxis('left').setPen(pg.mkPen(255, 0, 0, 255))
        # self.module_dialog._module_widget.errors_graph.getAxis('right').setPen(pg.mkPen(0, 0, 255, 255))
        #
        # ## Handle view resizing
        # def updateViews():
        #     ## view has resized; update auxiliary views to match
        #     p2.setGeometry(errors_viewbox.sceneBoundingRect())
        #     p2.linkedViewChanged(errors_viewbox, p2.XAxis)
        #
        # updateViews()
        # errors_viewbox.sigResized.connect(updateViews)
        # errors_legend.addItem(self.head_error_plot_handle, name='Heading Error')
        #
        # ## Initialize fb torque Plot
        # self.module_dialog._module_widget.fb_torques_graph.setTitle('Feedback Torques vs Time')
        # self.module_dialog._module_widget.fb_torques_graph.setXRange(-self.history_time, self.history_time / 10,
        #                                                             padding=0)
        # self.module_dialog._module_widget.fb_torques_graph.setYRange(-10, 10, padding=0)
        # self.module_dialog._module_widget.fb_torques_graph.setLabel('right', 'Torques [Nm]',
        #                                                            **{'font-size': '12pt'})
        # torques_viewbox = self.module_dialog._module_widget.fb_torques_graph.getViewBox()
        # torques_viewbox.setBackgroundColor((255, 255, 255, 200))
        # torques_viewbox.invertY(True)
        # torques_legend = pg.LegendItem(size=(120, 60), offset=None, horSpacing=30, verSpacing=-7,
        #                                pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        # torques_legend.setParentItem(torques_viewbox)
        # torques_legend.addItem(self.fb_torque_plot_handle, name='Feedback Torque')
        # torques_legend.addItem(self.ff_torque_plot_handle, name='Feedforward Torque')
        # torques_legend.addItem(self.loha_torque_plot_handle, name='LoHA Torque')
        # torques_legend.addItem(self.total_torque_plot_handle, name='Total Torque')
        # self.module_dialog._module_widget.fb_torques_graph.showGrid(True, True, 1)
        #
        # ## Initialize sw angle Plot
        # self.module_dialog._module_widget.sw_graph.setTitle('Steering Angles vs Time')
        # self.module_dialog._module_widget.sw_graph.setXRange(-self.history_time, self.history_time / 10, padding=0)
        # self.module_dialog._module_widget.sw_graph.setYRange(-185, 185, padding=0)
        # self.module_dialog._module_widget.sw_graph.showGrid(True, True, 1)
        # self.module_dialog._module_widget.sw_graph.setLabel('right', '<font>&Theta;SW</font>[deg]',
        #                                                    **{'font-size': '12pt'})
        # self.module_dialog._module_widget.sw_graph.setLabel('bottom', 'Time[s]', **{'font-size': '12pt'})
        # sw_des_viewbox = self.module_dialog._module_widget.sw_graph.getViewBox()
        # sw_des_viewbox.setBackgroundColor((255, 255, 255, 200))
        # sw_legend = pg.LegendItem(size=(120, 0), offset=None, horSpacing=30, verSpacing=-7,
        #                           pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        # sw_legend.setParentItem(sw_des_viewbox)
        # sw_legend.addItem(self.sw_des_plot_handle, name='Desired Steering Angle')
        # sw_legend.addItem(self.sw_act_plot_handle, name='Actual Steering Angle')

        return super().initialize()


    def stop(self):
        """stop the module"""
        # Will automatically go to READY as defined above in self.state_machine.set_automatic_transition
        self.module_dialog._module_widget.top_view_graph.clear()
        self.module_dialog._module_widget.torque_graph.clear()
        self.module_dialog._module_widget.errors_graph.clear()
        self.module_dialog._module_widget.fb_torques_graph.clear()
        self.module_dialog._module_widget.sw_graph.clear()

        return super().stop()