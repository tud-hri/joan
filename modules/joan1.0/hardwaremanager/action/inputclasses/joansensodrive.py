import multiprocessing as mp
import os
import time

from PyQt5 import uic, QtWidgets

from modules.hardwaremanager.action.hardwaremanagersettings import SensoDriveSettings
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.inputclasses.joan_sensodrive_communication import SensoDriveComm
from modules.hardwaremanager.action.inputclasses.joan_sensodrive_shared_variables import SensoDriveSharedValues
from modules.hardwaremanager.action.hwinputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules
from core.statesenum import State


class SensoDriveSettingsDialog(QtWidgets.QDialog):
    """
    Class for the settings Dialog of a SensoDrive, this class should pop up whenever it is asked by the user or when
    creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
    """

    def __init__(self, sensodrive_settings, parent=None):
        super().__init__(parent)
        self.sensodrive_settings = sensodrive_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/sensodrive_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)

        self.btn_apply.clicked.connect(self.update_parameters)

        self._display_values()

    def update_parameters(self):
        """
        Updates the parameters without closing the dialog
        """
        self.sensodrive_settings.endstops = self.spin_endstop_position.value()
        self.sensodrive_settings.torque_limit_between_endstops = self.spin_torque_limit_between_endstops.value()
        self.sensodrive_settings.torque_limit_beyond_endstops = self.spin_torque_limit_beyond_endstops.value()
        self.sensodrive_settings.friction = self.spin_friction.value()
        self.sensodrive_settings.damping = self.spin_damping.value()
        self.sensodrive_settings.spring_stiffness = self.spin_spring_stiffness.value()

    def accept(self):
        """
        Accepts the settings of the sensodrive and saves them internally.
        :return:
        """
        self.sensodrive_settings.endstops = self.spin_endstop_position.value()
        self.sensodrive_settings.torque_limit_between_endstops = self.spin_torque_limit_between_endstops.value()
        self.sensodrive_settings.torque_limit_beyond_endstops = self.spin_torque_limit_beyond_endstops.value()
        self.sensodrive_settings.friction = self.spin_friction.value()
        self.sensodrive_settings.damping = self.spin_damping.value()
        self.sensodrive_settings.spring_stiffness = self.spin_spring_stiffness.value()

        super().accept()

    def _display_values(self, settings_to_display=None):
        """
        Displays the currently used settings in the settings dialog.
        :param settings_to_display:
        :return:
        """
        if not settings_to_display:
            settings_to_display = self.sensodrive_settings

        self.spin_endstop_position.setValue(settings_to_display.endstops)
        self.spin_torque_limit_between_endstops.setValue(settings_to_display.torque_limit_between_endstops)
        self.spin_torque_limit_beyond_endstops.setValue(settings_to_display.torque_limit_beyond_endstops)
        self.spin_friction.setValue(settings_to_display.friction)
        self.spin_damping.setValue(settings_to_display.damping)
        self.spin_spring_stiffness.setValue(settings_to_display.spring_stiffness)

    def _set_default_values(self):
        """
        Sets the settings as they are described in Hardwaremanagersettings ->SensodriveSettings().
        :return:
        """
        self._display_values(SensoDriveSettings())


class JOANSensoDrive(BaseInput):
    """
    Main class for the SensoDrive input, inherits from BaseInput (as it should!)
    """

    def __init__(self, module_action, hardware_input_list_key, settings):
        super().__init__(hardware_input_type=HardwareInputTypes.SENSODRIVE, module_action=module_action)
        """
        Initializes the class, also uses some more parameters to keep track of how many sensodrives are connected
        :param hardware_manager_action:
        :param sensodrive_tab:
        :param nr_of_sensodrives:
        :param settings:
        """
        self.module_action = module_action
        self.hardware_input_list_key = hardware_input_list_key
        # Create the shared variables class
        self.sensodrive_shared_variables = SensoDriveSharedValues()

        # self.sensodrive_shared_variables.sensodrive_ID = nr_of_sensodrives

        # Torque safety variables
        self.counter = 0
        self.old_requested_torque = 0
        self.safety_checked_torque = 0
        self.t1 = 0
        self.torque_rate = 0

        self.currentInput = 'SensoDrive'
        self.settings = settings
        self.sensodrive_running = False

        self.settings_dialog = None

        # prepare for SensoDriveComm object (multiprocess)
        self.sensodrive_shared_variables.torque = self.settings.torque
        self.sensodrive_shared_variables.friction = self.settings.friction
        self.sensodrive_shared_variables.damping = self.settings.damping
        self.sensodrive_shared_variables.spring_stiffness = self.settings.spring_stiffness

        self.sensodrive_shared_variables.endstops = self.settings.endstops
        self.sensodrive_shared_variables.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
        self.sensodrive_shared_variables.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops

        self.init_event = mp.Event()
        self.close_event = mp.Event()
        self.turn_on_event = mp.Event()
        self.update_shared_variables_from_settings_event = mp.Event()
        self.turn_off_event = mp.Event()
        self.clear_error_event = mp.Event()

        # create SensoDriveComm object
        self.sensodrive_communication_process = SensoDriveComm(self.sensodrive_shared_variables, self.init_event,
                                                               self.turn_on_event, self.turn_off_event,
                                                               self.clear_error_event, self.close_event,
                                                               self.update_shared_variables_from_settings_event)
        self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_dialog_from_button)
        self._hardware_input_tab.btn_remove_hardware.clicked.connect(self.remove_hardware_input)
        self._hardware_input_tab.btn_on.clicked.connect(self.turn_motor_sensodrive_on)
        self._hardware_input_tab.btn_off.clicked.connect(self.turn_motor_sensodrive_off)
        self._hardware_input_tab.btn_clear_error.clicked.connect(self.clear_error)
        self._hardware_input_tab.btn_on.setEnabled(False)
        self._hardware_input_tab.btn_off.setEnabled(False)
        self._hardware_input_tab.btn_clear_error.setEnabled(False)
        self._hardware_input_tab.lbl_sensodrive_state.setText('Uninitialized')

        self._open_settings_dialog()
        
        if not self.sensodrive_communication_process.is_alive():
            self.init_event.set()
            self.sensodrive_communication_process.start()
            self.counter = 0
        self._hardware_input_tab.btn_on.setEnabled(True)
        self.lbl_state_update()

    @property
    def get_hardware_input_list_key(self):
        return self.hardware_input_list_key

    def state_change_listener(self):
        self.lbl_state_update()

    def update_shared_variables_from_settings(self):
        """
        Updates the settings that are saved internally. NOTE: this is different than with other input modules because
        we want to be ablte to set friction, damping and spring stiffnes parameters without closing the dialog window.
        :return:
        """
        self.sensodrive_shared_variables.endstops = self.settings.endstops
        self.sensodrive_shared_variables.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
        self.sensodrive_shared_variables.torque_limit_between_endstops = self.settings.torque_limit_between_endstops

        self.sensodrive_shared_variables.friction = self.settings.friction
        self.sensodrive_shared_variables.damping = self.settings.damping
        self.sensodrive_shared_variables.spring_stiffness = self.settings.spring_stiffness

        self.update_shared_variables_from_settings_event.set()


    def initialize(self):
        """
        Just updates the already initialized sensodrive.
        :return:
        """
        self.lbl_state_update()

    def _open_settings_dialog_from_button(self):
        """
        Opens and shows the settings dialog from the button on the tab
        :return:
        """
        self._open_settings_dialog()
        if self.settings_dialog:
            self.settings_dialog.show()

    def _open_settings_dialog(self):
        """
        Not used for this input
        """
        self.settings_dialog = SensoDriveSettingsDialog(self.settings)
        self.settings_dialog.btn_apply.clicked.connect(self.update_shared_variables_from_settings)

    def remove_hardware_input(self):
        """
        Removes the sensodrive from the widget and settings
        NOTE: calls 'self.remove_tab' which is a function of the BaseInput class, if you do_while_running not do_while_running this the tab will not
        actually disappear from the module.
        :return:
        """
        self.close_event.set()
        while self.close_event.is_set():
            pass
        self.sensodrive_communication_process.terminate()

        self.module_action.remove_hardware_input_device(self)

    def disable_remove_button(self):
        """
        Disables the sensodrive Remove button, (useful for example when you dont want to be able to remove an input when the
        simulator is running)
        :return:
        """
        if self._hardware_input_tab.btn_remove_hardware.isEnabled():
            self._hardware_input_tab.btn_remove_hardware.setEnabled(False)

    def enable_remove_button(self):
        """
        Enables the sensodrive remove button.
        :return:
        """
        if not self._hardware_input_tab.btn_remove_hardware.isEnabled():
            self._hardware_input_tab.btn_remove_hardware.setEnabled(True)

    def lbl_state_update(self):
        if self.sensodrive_shared_variables.sensodrive_motorstate == 0x10:
            self._hardware_input_tab.lbl_sensodrive_state.setStyleSheet("background-color: orange")
            self._hardware_input_tab.lbl_sensodrive_state.setText('Off')
            self._hardware_input_tab.btn_on.setEnabled(True)
            self._hardware_input_tab.btn_off.setEnabled(False)
            self._hardware_input_tab.btn_clear_error.setEnabled(False)
        elif self.sensodrive_shared_variables.sensodrive_motorstate == 0x14:
            self._hardware_input_tab.lbl_sensodrive_state.setStyleSheet("background-color: lightgreen")
            self._hardware_input_tab.lbl_sensodrive_state.setText('On')
            self._hardware_input_tab.btn_on.setEnabled(False)
            self._hardware_input_tab.btn_off.setEnabled(True)
            self._hardware_input_tab.btn_clear_error.setEnabled(False)
        elif self.sensodrive_shared_variables.sensodrive_motorstate == 0x18:
            self._hardware_input_tab.lbl_sensodrive_state.setStyleSheet("background-color: red")
            self._hardware_input_tab.lbl_sensodrive_state.setText('Error')
            self._hardware_input_tab.btn_on.setEnabled(False)
            self._hardware_input_tab.btn_off.setEnabled(False)
            self._hardware_input_tab.btn_clear_error.setEnabled(True)
        self._hardware_input_tab.repaint()

    def turn_motor_sensodrive_on(self):
        self.turn_on_event.set()
        time.sleep(0.05)
        self.lbl_state_update()

    def turn_motor_sensodrive_off(self):
        self.turn_off_event.set()
        time.sleep(0.05)
        self.lbl_state_update()


    def clear_error(self):
        self.clear_error_event.set()
        time.sleep(0.05)
        self.lbl_state_update()


    # def toggle_on_off(self):
    #     """
    #     If a PCAN dongle is connected and working will check what state the sensodrive is in and take the appropriate action
    #     (0x10 is ready, 0x14 is on and 0x18 is error)
    #     :return:
    #     """
    #     self.toggle_sensodrive_motor_event.set()
    #     # give the seperate core time to handle the signal
    #     time.sleep(0.02)
    #
    #     if self.sensodrive_shared_variables.sensodrive_motorstate == 0x10:
    #         self._hardware_input_tab.btn_on.setStyleSheet("background-color: orange")
    #         self._hardware_input_tab.btn_on.setText('Off')
    #     elif self.sensodrive_shared_variables.sensodrive_motorstate == 0x14:
    #         self._hardware_input_tab.btn_on.setStyleSheet("background-color: lightgreen")
    #         self._hardware_input_tab.btn_on.setText('On')
    #     elif self.sensodrive_shared_variables.sensodrive_motorstate == 0x18:
    #         self._hardware_input_tab.btn_on.setStyleSheet("background-color: red")
    #         self._hardware_input_tab.btn_on.setText('Clear Error')


    def do(self):
        """
        Basically acts as a portal of variables to the seperate sensodrive communication core. You can send info to this
        core using the shared variables in 'SensoDriveSharedValues' Class. NOTE THAT YOU SHOULD ONLY SET VARIABLES
        ON 1 SIDE!! Do not overwrite variables, if you want to send signals for events to the seperate core please use
        the multiprocessing.Events structure.
        :return: self._data a dictionary containing :
            self._data['steering_angle'] = self.sensodrive_shared_variables.steering_angle
            self._data['brake'] = self.sensodrive_shared_variables.brake
            self._data['throttle'] = self.sensodrive_shared_variables.throttle
            self._data['Handbrake'] = 0
            self._data['Reverse'] = 0
            self._data['requested_torque'] = requested_torque_by_controller
            self._data['checked_torque'] = self.safety_checked_torque
            self._data['torque_rate'] = self.torque_rate
        """

        # check whether we have a sw_controller that should be updated
        self._steering_wheel_control_data = self.module_action.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        self._carla_interface_data = self.module_action.read_news(JOANModules.CARLA_INTERFACE)

        self.lbl_state_update()

        try:
            requested_torque_by_controller = self._steering_wheel_control_data[
                self._carla_interface_data['ego_agents']['EgoVehicle 1']['vehicle_object'].selected_sw_controller]['sw_torque']
        except:
            requested_torque_by_controller = 0

        self.counter = self.counter + 1

        if self.counter == 5:
            [self.safety_checked_torque, self.torque_rate] = self.torque_check(
                requested_torque=requested_torque_by_controller, t1=self.t1, torque_limit_mnm=20000,
                torque_rate_limit_nms=150)
            self.t1 = int(round(time.time() * 1000))
            self.counter = 0

        # Write away torque parameters and torque checks
        self._data['requested_torque'] = requested_torque_by_controller
        self._data['checked_torque'] = self.safety_checked_torque
        self._data['torque_rate'] = self.torque_rate
        self._data['measured_torque'] = self.sensodrive_shared_variables.measured_torque

        # Handle all shared parameters with the seperate sensodrive communication core
        # Get parameters
        self._data['steering_angle'] = self.sensodrive_shared_variables.steering_angle
        self._data['steering_rate'] = self.sensodrive_shared_variables.steering_rate
        self._data['brake'] = self.sensodrive_shared_variables.brake
        self._data['throttle'] = self.sensodrive_shared_variables.throttle
        self._data['Handbrake'] = 0
        self._data['Reverse'] = 0

        # print(extra_endstop)
        #print('req:= ', requested_torque_by_controller, 'safe = ', self.safety_checked_torque)
        self.sensodrive_shared_variables.torque = self.safety_checked_torque
        self.sensodrive_shared_variables.friction = self.settings.friction
        self.sensodrive_shared_variables.damping = self.settings.damping

        self.sensodrive_shared_variables.endstops = self.settings.endstops
        self.sensodrive_shared_variables.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
        self.sensodrive_shared_variables.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
        self.sensodrive_shared_variables.spring_stiffness = self.settings.spring_stiffness

        # Lastly we also need to write the spring stiffness in data for controller purposes
        self._data['spring_stiffness'] = self.sensodrive_shared_variables.spring_stiffness

        return self._data

    def torque_check(self, requested_torque, t1, torque_rate_limit_nms, torque_limit_mnm):
        """
        Checks the torque in 2 ways, one the max capped torque
        And the torque rate.
        If the max torque is too high it will cap, if the torque_rate is too high the motor will shut off
        """
        t2 = int(round(time.time() * 1000))

        torque_rate = (self.old_requested_torque - requested_torque) / ((t2 - t1) * 1000) * 1000  # Nm/s

        if abs(torque_rate) > torque_rate_limit_nms:
            print('TORQUE RATE TOO HIGH! TURNING OFF SENSODRIVE')
            self.shut_off_sensodrive()

        if requested_torque > torque_limit_mnm:
            checked_torque = torque_limit_mnm
        elif requested_torque < -torque_limit_mnm:
            checked_torque = -torque_limit_mnm
        else:
            checked_torque = requested_torque

        # update torque for torque rate calc
        self.old_requested_torque = requested_torque

        return [checked_torque, torque_rate]
