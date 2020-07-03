from PyQt5 import QtCore
import sys
import glob
import os
import random
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
    def __init__(self, agentmanager_action):
        self.module_action = agentmanager_action
        self._spawned = False
        self._vehicle_tab = None
        self.car_data = {}

    def unpack_vehicle_data(self):
        try:
            #spatial:
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
            self.car_data['forward_vector_x_component'] = self.spawned_vehicle.get_transform().rotation.get_forward_vector().x
            self.car_data['forward_vector_y_component'] = self.spawned_vehicle.get_transform().rotation.get_forward_vector().y
            self.car_data['forward_vector_z_component'] = self.spawned_vehicle.get_transform().rotation.get_forward_vector().z


            #inputs
            last_applied_vehicle_control = self.spawned_vehicle.get_control()
            self.car_data['throttle_input'] = last_applied_vehicle_control.throttle
            self.car_data['brake_input'] = last_applied_vehicle_control.brake
            self.car_data['steering_input'] = last_applied_vehicle_control.steer
            self.car_data['reverse'] = last_applied_vehicle_control.reverse
            self.car_data['manual_gear_shift'] = last_applied_vehicle_control.manual_gear_shift
            self.car_data['gear'] = last_applied_vehicle_control.gear

        except:
            pass

        return self.car_data

    def spawn_car(self):
        self._BP = random.choice(self.module_action.vehicle_bp_library.filter("vehicle." + self.settings._selected_car))
        self._control = carla.VehicleControl()
        try:
            spawnpointnr = self.settings._spawn_point_nr
            self.spawned_vehicle = self.module_action.world.spawn_actor(self._BP, self.module_action.spawnpoints[spawnpointnr])
            self._vehicle_tab.btn_spawn.setEnabled(False)
            self._vehicle_tab.btn_destroy.setEnabled(True)
            # self._vehicle_tab.spin_spawn_points.setEnabled(False)
            # self._vehicle_tab.combo_car_type.setEnabled(False)
            #self.get_available_inputs()
            self._spawned = True
        except Exception as inst:
            print('Could not spawn car:', inst)
            self._vehicle_tab.btn_spawn.setEnabled(True)
            self._vehicle_tab.btn_destroy.setEnabled(False)
            # self._vehicle_tab.spin_spawn_points.setEnabled(True)
            # self._vehicle_tab.combo_car_type.setEnabled(True)
            self._spawned = False

    def destroy_car(self):
        try:
            self._spawned = False
            self.spawned_vehicle.destroy()
            self._vehicle_tab.btn_spawn.setEnabled(True)
            self._vehicle_tab.btn_destroy.setEnabled(False)
            # self._vehicle_tab.spin_spawn_points.setEnabled(True)
            # self._vehicle_tab.combo_car_type.setEnabled(True)
        except Exception as inst:
            self._spawned = True
            print('Could not destroy spawn car:', inst)
            self._vehicle_tab.btn_spawn.setEnabled(False)
            self._vehicle_tab.btn_destroy.setEnabled(True)
            # self._vehicle_tab.spin_spawn_points.setEnabled(False)
            # self._vehicle_tab.combo_car_type.setEnabled(False)

    @property
    def vehicle_id(self):
        return self._BP.id

    @property
    def spawned(self):
        return self._spawned

    @property
    def vehicle_tab(self):
        return self._vehicle_tab

    @property
    def vehicle_id(self):
        return self._BP.id


