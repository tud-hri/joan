from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
import numpy as np
import pyqtgraph as pg
import math
from PyQt5 import QtGui

class ControllerPlotterDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.CONTROLLER_PLOTTER, module_manager=module_manager, parent=parent)
        self.data = {}

    def update_dialog(self):
        "update de hele zooi hier"
        for keys in self.module_manager.singleton_settings.all_settings_keys:
            self.data[keys] = self.module_manager.singleton_news.read_news(keys)

        print(self.data[JOANModules.HARDWARE_MANAGER].inputs['Keyboard_1'].brake)

        # data_from_haptic_controller_manager = self.data[JOANModules.HAPTIC_CONTROLLER_MANAGER].controllers['FDCA_1']
        data_from_hardware_manager = self.data[JOANModules.HARDWARE_MANAGER].inputs['Keyboard_1']
        # data_from_carla_interface = self.data[JOANModules.CARLA_INTERFACE].agents['EgoVehicle_1']

        steering_ang = math.degrees(data_from_hardware_manager.steering_angle)
        sw_actual = math.degrees(data_from_hardware_manager.steering_angle)
        sw_stiffness = math.radians(1)

        # sw actual plot
        if self._module_widget.check_sw_act.isChecked():
            self.module_manager.plot_data_sw_act_y.append(sw_actual)
            self.module_manager.plot_data_sw_act_y.pop(0)
            self.module_manager.sw_act_plot_handle.setData(x=self.module_manager.time_list, y=self.module_manager.plot_data_sw_act_y, size=5,
                                            pen=pg.mkPen((217, 83, 25, 200), width=3), brush=pg.mkBrush((217, 83, 25, 200)),
                                            symbol=None, symbolBrush=pg.mkBrush((217, 83, 25, 200)),
                                            symbolPen=pg.mkPen((217, 83, 25, 200)), symbolSize=3)
        else:
            self.module_manager.sw_act_plot_handle.setData(pen=pg.mkPen((217, 83, 25, 0)))


    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """

        data_from_haptic_controller_manager = self.data[JOANModules.HAPTIC_CONTROLLER_MANAGER].controllers['FDCA_1']
        data_from_hardware_manager = self.data[JOANModules.HARDWARE_MANAGER].inputs['Keyboard_1']
        data_from_carla_interface = self.data[JOANModules.CARLA_INTERFACE].agents['EgoVehicle_1']

        steering_ang = math.degrees(data_from_hardware_manager.steering_angle)
        sw_actual = math.degrees(data_from_hardware_manager.steering_angle)
        sw_stiffness = math.radians(1)

        # try assigning variables:
        # from hardware manager
        # try:
        #     if 'SensoDrive 1' in data_from_hardware_manager.keys():
        #         ## sensodrive
        #         steering_ang = math.degrees(data_from_hardware_manager['SensoDrive 1']['steering_angle'])
        #         actual_torque = data_from_hardware_manager['SensoDrive 1']['measured_torque']
        #         sw_actual = math.degrees(data_from_hardware_manager['SensoDrive 1']['steering_angle'])
        #         sw_stiffness = math.radians(data_from_hardware_manager['SensoDrive 1']['spring_stiffness'])
        #     elif 'Joystick 1' in data_from_hardware_manager.keys():
        #         ## joystick
        #         steering_ang = math.degrees(data_from_hardware_manager['Joystick 1']['steering_angle'])
        #         sw_actual = math.degrees(data_from_hardware_manager['Joystick 1']['steering_angle'])
        #         sw_stiffness = math.radians(1)
        #     elif 'Keyboard 1' in data_from_hardware_manager.keys():
        #         ## keyboardinput
        #         steering_ang = math.degrees(data_from_hardware_manager['Keyboard 1']['steering_angle'])
        #         sw_actual = math.degrees(data_from_hardware_manager['Keyboard 1']['steering_angle'])
        #         sw_stiffness = math.radians(1)
        #     else:
        #         steering_ang = 0
        #         sw_actual = 0
        #         sw_stiffness = 0

        # except KeyError or TypeError:
        #     steering_ang = 0
        #     sw_actual = 0
        #     sw_stiffness = math.radians(1)

        # from steeringwheel controller
        try:
            lat_error = data_from_haptic_controller_manager['FDCA 1']['lat_error']
            sw_des = math.degrees(data_from_haptic_controller_manager['FDCA 1']['sw_angle_desired_radians'])
            heading_error = math.degrees(data_from_haptic_controller_manager['FDCA 1']['heading_error'])
            ff_torque = data_from_haptic_controller_manager['FDCA 1']['ff_torque']
            fb_torque = data_from_haptic_controller_manager['FDCA 1']['fb_torque']
            loha_torque = data_from_haptic_controller_manager['FDCA 1']['loha_torque']
            req_torque = data_from_haptic_controller_manager['FDCA 1']['sw_torque']


        except KeyError or TypeError:
            lat_error = 0
            sw_des = 0
            heading_error = 0
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
                    self.road_lanewidth.append(waypoints[0].lane_width)

                for waypoints in next_waypoints:
                    self.plot_data_road_x.append(waypoints[0].transform.location.x)
                    self.plot_data_road_y.append(waypoints[0].transform.location.y)
                    self.road_lanewidth.append(waypoints[0].lane_width)

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

                #Set plotranges (KEEP IT SQUARE)
                max_plotrange_x = self.plot_data_road_x[24] + 20
                min_plotrange_x = self.plot_data_road_x[24] - 20
                max_plotrange_y = self.plot_data_road_y[24] + 20
                min_plotrange_y = self.plot_data_road_y[24] - 20

                #Rotate plots according to the road orientation (makes sure we keep driving 'upwards')
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
                rot_carSymbol = angle_rot.map(self.carSymbol)

                self.car_trace_x.append(vehicle_location.x)
                self.car_trace_y.append(vehicle_location.y)
                self.car_trace_psi.append(rot_carSymbol)

                self.plot_data_lat_error_topview_x = [vehicle_location.x, vehicle_location.x + math.sin(self.plot_data_road_psi[24]) * lat_error]
                self.plot_data_lat_error_topview_y = [vehicle_location.y, vehicle_location.y + math.cos(self.plot_data_road_psi[24]) * lat_error]

                length = 50
                upper = vehicle_rotation + heading_error
                lower = vehicle_rotation
                angles = [lower + x * (upper - lower) / length for x in range(length)]

                for angle in angles:
                    self.plot_data_heading_error_top_view_x.append(vehicle_location.x + math.cos(math.radians(angle))  * 10)
                    self.plot_data_heading_error_top_view_y.append(vehicle_location.y + math.sin(math.radians(angle)) * 10)


                self.plot_data_car_heading_line_x = [vehicle_location.x, vehicle_location.x + math.cos(math.radians(vehicle_rotation)) * 18]
                self.plot_data_car_heading_line_y = [vehicle_location.y, vehicle_location.y + math.sin(math.radians(vehicle_rotation)) * 18]

                self.plot_data_HCR_heading_line_x = [vehicle_location.x, vehicle_location.x + math.cos(math.radians(vehicle_rotation + heading_error)) * 18]
                self.plot_data_HCR_heading_line_y = [vehicle_location.y, vehicle_location.y + math.sin(math.radians(vehicle_rotation + heading_error)) * 18]

                if len(self.car_trace_x) > self.car_trace_length:
                    self.car_trace_x.pop(0)
                    self.car_trace_y.pop(0)
                    self.car_trace_psi.pop(0)

                self.road_outer_plot_handle.setData(x=self.plot_data_road_x_outer[0:-2], y=self.plot_data_road_y_outer[0:-2])
                self.road_inner_plot_handle.setData(x=self.plot_data_road_x_inner[0:-2], y=self.plot_data_road_y_inner[0:-2])
                self.road_plot_handle.setData(x=self.plot_data_road_x[0:-2], y=self.plot_data_road_y[0:-2])
                self.topview_heading_error_plot_handle.setData(x= self.plot_data_heading_error_top_view_x, y = self.plot_data_heading_error_top_view_y)
                self.module_dialog.module_widget.top_view_graph.setXRange(min_plotrange_x, max_plotrange_x, padding=0)
                self.module_dialog.module_widget.top_view_graph.setYRange(min_plotrange_y, max_plotrange_y, padding=0)

                #Clear lists so we can append them again for the next loop
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

            else:
                self.module_dialog.module_widget.top_view_graph.clear()


        #set data
        self.auto_position_plot_handle.setData(x=self.car_trace_x, y=self.car_trace_y, symbol=self.car_trace_psi, symbolPen=self.car_pens, symbolBrush=self.car_brushes)
        self.topview_lat_error_plot_handle.setData(x=self.plot_data_lat_error_topview_x, y=self.plot_data_lat_error_topview_y)
        self.topview_heading_line_plot_handle.setData(x=self.plot_data_car_heading_line_x, y=self.plot_data_car_heading_line_y)
        self.topview_HCR_heading_line_plot_handle.setData(x=self.plot_data_HCR_heading_line_x, y=self.plot_data_HCR_heading_line_y)


        # Big Torque vs steering Angle plot
        self.plot_data_torque_x.append(steering_ang)
        #only append the actual measured torque if there is a sensodrive, else plot the requested torque by the controller
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
            self.total_torque_plot_handle.setData(x=self.time_list, y=self.plot_data_total_torque_y, size=2,
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
