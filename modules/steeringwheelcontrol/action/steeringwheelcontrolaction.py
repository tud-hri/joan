from core.joanmoduleaction import JoanModuleAction
from core.statesenum import State
from modules.joanmodules import JOANModules
from .steeringwheelcontrolsettings import SteeringWheelControlSettings
from .swcontrollertypes import SWControllerTypes


class SteeringWheelControlAction(JoanModuleAction):

    def __init__(self, millis=10):
        super().__init__(module=JOANModules.STEERING_WHEEL_CONTROL, millis=millis)

        self.settings = SteeringWheelControlSettings(module_enum=JOANModules.STEERING_WHEEL_CONTROL)
        self.settings.before_load_settings.connect(self.prepare_load_settings)
        self.settings.load_settings_done.connect(self.apply_loaded_settings)
        self.share_settings(self.settings)

        self._controllers = {}

        # Setup state machine transition conditions
        self.state_machine.add_state_change_listener(self._state_change_listener)

        # set up news
        self.data = {}
        self.write_news(news=self.data)

    def _state_change_listener(self):
        sim_data_in = self.read_news(JOANModules.CARLA_INTERFACE)
        hw_data_in = self.read_news(JOANModules.HARDWARE_MANAGER)
        for controller in self._controllers:
            if 'ego_agents' in sim_data_in:
                if 'EgoVehicle 1' in sim_data_in['ego_agents']:
                    self.data[controller] = self._controllers[controller].calculate(
                        sim_data_in['ego_agents']['EgoVehicle 1']['vehicle_object'], hw_data_in)
                else:
                    self.data[controller] = None

        if self.state_machine.current_state is State.RUNNING:
            for controller in self._controllers:
                self._controllers[controller].settings_dialog.cmbbox_hcr_selection.setEnabled(False)

        else:
            for controller in self._controllers:
                self._controllers[controller].settings_dialog.cmbbox_hcr_selection.setEnabled(True)

        self.write_news(self.data)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        sim_data_in = self.read_news(JOANModules.CARLA_INTERFACE)
        hw_data_in = self.read_news(JOANModules.HARDWARE_MANAGER)

        # FOR NOW WE ONLY TRY TO APPLY CONTROLLER ON 1 CAR CAUSE MULTIPLE IS TOTAL MAYHEM
        for controller in self._controllers:
            if 'ego_agents' in sim_data_in:
                if 'EgoVehicle 1' in sim_data_in['ego_agents']:
                    self.data[controller] = self._controllers[controller].calculate(sim_data_in['ego_agents']['EgoVehicle 1']['vehicle_object'], hw_data_in)

        # for controller in self._controllers:
        #     if sim_data_in['vehicles'] is not None:
        #         for vehicle_object in sim_data_in['vehicles']:
        #             self.data[controller] = self._controllers[controller].do(vehicle_object, hw_data_in)
        #     else:
        #         self.data[controller] = self._controllers[controller].do(None, hw_data_in)
        # print(self.data)

        self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        try:
            if self.state_machine.current_state == State.IDLE:
                if len(self._controllers) != 0:
                    for controllers in self._controllers:
                        self._controllers[controllers].initialize()
                    self.state_machine.request_state_change(State.READY, 'You can now run the module')
                else:
                    self.state_machine.request_state_change(State.ERROR, 'No controllers to initialize')
            elif self.state_machine.current_state == State.ERROR:
                self.state_machine.request_state_change(State.IDLE)

        except RuntimeError:
            return False
        return super().initialize()

    def prepare_load_settings(self):
        """
        Prepare the module for new settings: remove all 'old' hardware from the list
        :return:
        """
        # remove_input_device all current controllers first:
        for controller in list(self._controllers.keys()):
            self.remove_controller(self._controllers[controller])

    def apply_loaded_settings(self):
        """
        Create hardware inputs based on the loaded settings
        :return:
        """
        for pd_controller_settings in self.settings.pd_controllers:
            self.add_controller(SWControllerTypes.PD_SWCONTROLLER, pd_controller_settings)

        for fdca_controller_settings in self.settings.fdca_controllers:
            self.add_controller(SWControllerTypes.FDCA_SWCONTROLLER, fdca_controller_settings)

        self.initialize()

    def add_controller(self, controller_type, controller_settings=None):
        # set the module to idle because we need to reinitialize our controllers!
        self.state_machine.request_state_change(State.IDLE, 'You can now add more and reinitialize controllers')
        number_of_controllers = sum([bool(controller_type.__str__() in k) for k in self._controllers.keys()]) + 1
        controller_name = controller_type.__str__() + ' ' + str(number_of_controllers)

        # add appropriate settings
        if not controller_settings:
            controller_settings = controller_type.settings
            if controller_type == SWControllerTypes.PD_SWCONTROLLER:
                self.settings.pd_controllers.append(controller_settings)
            if controller_type == SWControllerTypes.FDCA_SWCONTROLLER:
                self.settings.fdca_controllers.append(controller_settings)

            self._controllers[controller_name] = controller_type.klass(self, controller_name, controller_settings)
            self._controllers[controller_name].get_controller_tab.controller_groupbox.setTitle(controller_name)
            self._controllers[controller_name].update_trajectory_list()
            self.module_dialog.module_widget.sw_controller_list_layout.addWidget(
                self._controllers[controller_name].get_controller_tab)

            self._controllers[controller_name]._open_settings_dialog_from_button()

        else:
            self._controllers[controller_name] = controller_type.klass(self, controller_name, controller_settings)
            self._controllers[controller_name].get_controller_tab.controller_groupbox.setTitle(controller_name)
            self._controllers[controller_name].update_trajectory_list()
            self.module_dialog.module_widget.sw_controller_list_layout.addWidget(
                self._controllers[controller_name].get_controller_tab)
            self._controllers[controller_name]._open_settings_dialog()

        self._state_change_listener()

        return self._controllers[controller_name].get_controller_tab

    def remove_controller(self, controller):
        # remove_input_device controller from the news
        try:
            del self.data[controller.get_controller_list_key]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        # remove_input_device controller settings
        try:
            self.settings.remove_controller(
                self._controllers[controller.get_controller_list_key].settings)
        except ValueError:  # depends if right controller list is present
            pass

        try:
            self.settings.remove_controller(
                self._controllers[controller.get_controller_list_key].settings)
        except ValueError:  # depends if right controller list is present
            pass

        # remove dialog
        self._controllers[controller.get_controller_list_key].get_controller_tab.setParent(None)

        # delete object
        del self._controllers[controller.get_controller_list_key]

        # remove controller from data
        try:
            del self.data[controller]
        except KeyError:  # data is only present if the hardware manager ran since the hardware was added
            pass

        if not self._controllers:
            self.stop()

    def start(self):
        try:
            self.state_machine.request_state_change(State.RUNNING, 'Module Running')
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            try:
                self.state_machine.request_state_change(State.IDLE)
                if len(self._controllers) != 0:
                    self.state_machine.request_state_change(State.READY)
            except RuntimeError:
                return False
        except RuntimeError:
            return False
        return super().stop()

    @property
    def controllers(self):
        return self._controllers

    @property
    def current_controller(self):
        return self._current_controller
