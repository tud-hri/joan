import glob
import os
import random
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox

msg_box = QMessageBox()
msg_box.setTextFormat(QtCore.Qt.RichText)

try:
    sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    import carla

except IndexError:
    msg_box.setText("""
                <h3> Could not find the carla python API! </h3>
                <h3> Check whether you copied the egg file correctly, reference:
            <a href=\"https://joan.readthedocs.io/en/latest/setup-run-joan/#getting-necessary-python3-libraries-to-run-joan\">https://joan.readthedocs.io/en/latest/setup-run-joan/#getting-necessary-python3-libraries-to-run-joan</a>
            </h3>
            """)
    msg_box.exec()
    pass


class Basevehicle:
    """
    The base class of any vehicle or 'agent', any agent of which you want to collect data should inherit from this class
    """

    def __init__(self, carlainterface_action, name=''):
        """
        Initializes class
        :param carlainterface_action:
        """
        self.module_action = carlainterface_action
        self._spawned = False
        self.vehicle_tab_widget = None
        self.car_data = {}
        self.spawned_vehicle = None
        self.name = name

    def unpack_vehicle_data(self):
        try:
            # vehicle object
            self.car_data['vehicle_object'] = self

            # spatial:
            self.car_data['x_pos'] = self.spawned_vehicle.get_transform().location.x
            self.car_data['y_pos'] = self.spawned_vehicle.get_transform().location.y
            self.car_data['z_pos'] = self.spawned_vehicle.get_transform().location.z
            self.car_data['yaw'] = self.spawned_vehicle.get_transform().rotation.yaw
            self.car_data['pitch'] = self.spawned_vehicle.get_transform().rotation.pitch
            self.car_data['roll'] = self.spawned_vehicle.get_transform().rotation.roll
            self.car_data['x_ang_vel'] = self.spawned_vehicle.get_angular_velocity().x
            self.car_data['y_ang_vel'] = self.spawned_vehicle.get_angular_velocity().y
            self.car_data['z_ang_vel'] = self.spawned_vehicle.get_angular_velocity().z
            self.car_data['x_vel'] = self.spawned_vehicle.get_velocity().x
            self.car_data['y_vel'] = self.spawned_vehicle.get_velocity().y
            self.car_data['z_vel'] = self.spawned_vehicle.get_velocity().z
            self.car_data['x_acc'] = self.spawned_vehicle.get_acceleration().x
            self.car_data['y_acc'] = self.spawned_vehicle.get_acceleration().y
            self.car_data['z_acc'] = self.spawned_vehicle.get_acceleration().z
            self.car_data['forward_vector_x_component'] = \
                self.spawned_vehicle.get_transform().rotation.get_forward_vector().x
            self.car_data['forward_vector_y_component'] \
                = self.spawned_vehicle.get_transform().rotation.get_forward_vector().y
            self.car_data['forward_vector_z_component'] \
                = self.spawned_vehicle.get_transform().rotation.get_forward_vector().z

            # inputs
            last_applied_vehicle_control = self.spawned_vehicle.get_control()
            self.car_data['throttle_input'] = last_applied_vehicle_control.throttle
            self.car_data['brake_input'] = last_applied_vehicle_control.brake
            self.car_data['steering_input'] = last_applied_vehicle_control.steer
            self.car_data['reverse'] = last_applied_vehicle_control.reverse
            self.car_data['manual_gear_shift'] = last_applied_vehicle_control.manual_gear_shift
            self.car_data['gear'] = last_applied_vehicle_control.gear

        except:
            # vehicle object
            self.car_data['vehicle_object'] = self
            pass

        return self.car_data

    def spawn_car(self):
        """
        Tries to spawn the agent/vehicle
        :return:
        """
        self._BP = random.choice(self.module_action.vehicle_bp_library.filter("vehicle." + self.settings.selected_car))
        self._control = carla.VehicleControl()
        torque_curve = []
        gears = []

        torque_curve.append(carla.Vector2D(x=0, y=600))
        torque_curve.append(carla.Vector2D(x=14000, y=600))
        gears.append(carla.GearPhysicsControl(ratio=7.73, down_ratio=0.5, up_ratio=1))

        try:
            self.spawned_vehicle = self.module_action.world.spawn_actor(self._BP, self.module_action.spawnpoints[
                self.settings.selected_spawnpoint])
            physics = self.spawned_vehicle.get_physics_control()
            physics.torque_curve = torque_curve
            physics.max_rpm = 14000
            physics.moi = 1.5
            physics.final_ratio = 1
            physics.clutch_strength = 1000  # very big no clutch
            physics.final_ratio = 1  # ratio from transmission to wheels
            physics.forward_gears = gears
            physics.mass = 2316
            physics.drag_coefficient = 0.24
            physics.gear_switch_time = 0
            self.spawned_vehicle.apply_physics_control(physics)

            self.vehicle_tab_widget.btn_spawn.setEnabled(False)
            self.vehicle_tab_widget.btn_destroy.setEnabled(True)
            self._spawned = True
        except Exception as inst:
            print('Could not spawn car:', inst)
            self.vehicle_tab_widget.btn_spawn.setEnabled(True)
            self.vehicle_tab_widget.btn_destroy.setEnabled(False)
            self._spawned = False

    def destroy_car(self):
        """
        Tries to destroy the agent/car
        :return:
        """
        try:
            if self._spawned:
                self.spawned_vehicle.destroy()
                self._spawned = False
            self.vehicle_tab_widget.btn_spawn.setEnabled(True)
            self.vehicle_tab_widget.btn_destroy.setEnabled(False)
        except Exception as inst:
            self._spawned = True
            print('Could not destroy spawn car:', inst)
            self.vehicle_tab_widget.btn_spawn.setEnabled(False)
            self.vehicle_tab_widget.btn_destroy.setEnabled(True)

    @property
    def vehicle_id(self):
        return self._BP.id

    @property
    def spawned(self):
        return self._spawned

    @property
    def vehicle_tab(self):
        return self.vehicle_tab_widget

    @property
    def vehicle_id(self):
        return self._BP.id
