from .basevehicle import Basevehicle
from modules.joanmodules import JOANModules
from PyQt5 import uic
import os


class Egovehicle(Basevehicle):
    def __init__(self, agent_manager_action, car_nr, nr_spawn_points, tags):
        super().__init__(agent_manager_action)

        self._vehicle_tab = uic.loadUi(uifile=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../vehicletab.ui"))
        self._vehicle_tab.group_car.setTitle('Car ' + str(car_nr+1))
        self._spawned = False
        self._hardware_data = {}
        self._sw_controller_data = {}
        self._vehicle_nr = 'Car ' + str(car_nr+1)
        self._sw_controller = self._vehicle_tab.combo_sw_controller.currentText()

        self._vehicle_tab.spin_spawn_points.setRange(0, nr_spawn_points)
        self._vehicle_tab.spin_spawn_points.lineEdit().setReadOnly(True)
        self._vehicle_tab.btn_destroy.setEnabled(False)
        self._vehicle_tab.combo_input.currentTextChanged.connect(self.update_input)
        self._vehicle_tab.combo_sw_controller.currentTextChanged.connect(self.update_sw_controller)

        self._vehicle_tab.btn_spawn.clicked.connect(self.spawn_car)
        self._vehicle_tab.btn_destroy.clicked.connect(self.destroy_car)
        self._vehicle_tab.btn_remove_ego_agent.clicked.connect(self.remove_ego_agent)

        for item in tags:
            self._vehicle_tab.combo_car_type.addItem(item)

        self._selected_input = str('None')

    @property
    def vehicle_tab(self):
        return self._vehicle_tab

    @property
    def selected_input(self):
        return self._selected_input

    @property
    def selected_sw_controller(self):
        return self._sw_controller

    @property
    def vehicle_id(self):
        return self._BP.id

    @property
    def vehicle_nr(self):
        return self._vehicle_nr

    def update_sw_controller(self):
        self._sw_controller = self._vehicle_tab.combo_sw_controller.currentText()

    def update_input(self):
        self._selected_input = self._vehicle_tab.combo_input.currentText()

    def get_available_inputs(self):
        self._vehicle_tab.combo_input.clear()
        self._vehicle_tab.combo_input.addItem('None')
        self._hardware_data = self.module_action.read_news(JOANModules.HARDWARE_MANAGER)
        for keys in self._hardware_data:
            self._vehicle_tab.combo_input.addItem(str(keys))

    def get_available_controllers(self):
        self._vehicle_tab.combo_sw_controller.clear()
        self._vehicle_tab.combo_sw_controller.addItem('None')
        self._sw_controller_data = self.module_action.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        for keys in self._sw_controller_data:
            self._vehicle_tab.combo_sw_controller.addItem(str(keys))


    def destroy_inputs(self):
        self._vehicle_tab.combo_input.clear()
        self._vehicle_tab.combo_input.addItem('None')


    def apply_control(self, data):
        if self._selected_input != 'None':
            self._control.steer = data[self._selected_input]['SteeringInput'] / 450
            self._control.throttle = data[self._selected_input]['ThrottleInput'] / 100
            self._control.brake = data[self._selected_input]['BrakeInput'] / 100
            self._control.reverse = data[self._selected_input]['Reverse']
            self._control.hand_brake = data[self._selected_input]['Handbrake']
            self.spawned_vehicle.apply_control(self._control)

    def remove_ego_agent(self):
        self._vehicle_tab.setParent(None)
        self.destroy_car()

        self.module_action.vehicles.remove(self)
