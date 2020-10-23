import multiprocessing as mp
import os
import time
import math
from ctypes import *
from PyQt5 import uic, QtWidgets

from modules.hardwaremp.hardwaremp_settings import SensoDriveSettings
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.joanmodules import JOANModules
from modules.hardwaremp.hardwaremp_inputclasses.PCANBasic import *

"""
These global parameters are used to make the message ID's more identifiable than just the hex nr.
"""
INITIALIZATION_MESSAGE_ID = 0x200
INITIALIZATION_MESSAGE_LENGTH = 8
STATE_MESSAGE_RECEIVE_ID = 0x210

STEERINGWHEEL_MESSAGE_SEND_ID = 0x201
STEERINGWHEEL_MESSAGE_RECEIVE_ID = 0x211
STEERINGWHEEL_MESSAGE_LENGTH = 8

PEDAL_MESSAGE_SEND_ID = 0x20C
PEDAL_MESSAGE_RECEIVE_ID = 0x21C
PEDAL_MESSAGE_LENGTH = 2

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
        Sets the settings as they are described in hardwarempsettings ->SensodriveSettings().
        :return:
        """
        self._display_values(SensoDriveSettings())

#
# class JOANSensoDrive(BaseInput):
#     """
#     Main class for the SensoDrive input, inherits from BaseInput (as it should!)
#     """
#
#     def __init__(self, module_manager, hardware_input_list_key, settings):
#         super().__init__(hardware_input_type=HardwareInputTypes.SENSODRIVE, module_manager=module_manager)
#         """
#         Initializes the class, also uses some more parameters to keep track of how many sensodrives are connected
#         :param hardware_manager_action:
#         :param sensodrive_tab:
#         :param nr_of_sensodrives:
#         :param settings:
#         """
#         self.module_manager = module_manager
#         self.hardware_input_list_key = hardware_input_list_key
#         # Create the shared variables class
#         self.sensodrive_communication_values = SensoDriveCommunicationValues()
#
#         # self.sensodrive_communication_values.sensodrive_ID = nr_of_sensodrives
#
#         # Torque safety variables
#         self.counter = 0
#         self.old_requested_torque = 0
#         self.safety_checked_torque = 0
#         self.t1 = 0
#         self.torque_rate = 0
#
#         self.currentInput = 'SensoDrive'
#         self.settings = settings
#         self.sensodrive_running = False
#
#         self.settings_dialog = None
#
#         # # prepare for SensoDriveComm object (multiprocess)
#         # self.sensodrive_communication_values.torque = self.settings.torque
#         # self.sensodrive_communication_values.friction = self.settings.friction
#         # self.sensodrive_communication_values.damping = self.settings.damping
#         # self.sensodrive_communication_values.spring_stiffness = self.settings.spring_stiffness
#         #
#         # self.sensodrive_communication_values.endstops = self.settings.endstops
#         # self.sensodrive_communication_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
#         # self.sensodrive_communication_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
#         #
#         #
#         #
#         # # create SensoDriveComm object
#         # # self.sensodrive_communication_process = SensoDriveComm(self.sensodrive_communication_values, self.module_manager.shared_variables.init_event,
#         # #                                                        self.module_manager.shared_variables.turn_on_event, self.module_manager.shared_variables.turn_off_event,
#         # #                                                        self.module_manager.shared_variables.clear_error_event, self.module_manager.shared_variables.close_event,
#         # #                                                        self.module_manager.shared_variables.update_shared_variables_from_settings_event)
#         self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_dialog)
#         self._hardware_input_tab.btn_settings.clicked.connect(self._open_settings_dialog_from_button)
#         self._hardware_input_tab.btn_remove_hardware.clicked.connect(self.remove_hardware_input)
#         self._hardware_input_tab.btn_on.clicked.connect(self.turn_motor_sensodrive_on)
#         self._hardware_input_tab.btn_off.clicked.connect(self.turn_motor_sensodrive_off)
#         self._hardware_input_tab.btn_clear_error.clicked.connect(self.clear_error)
#         # self._hardware_input_tab.btn_on.setEnabled(False)
#         # self._hardware_input_tab.btn_off.setEnabled(False)
#         # self._hardware_input_tab.btn_clear_error.setEnabled(False)
#         # self._hardware_input_tab.lbl_sensodrive_state.setText('Uninitialized')
#
#         self._open_settings_dialog()
#
#         # if not self.sensodrive_communication_process.is_alive():
#         #     self.module_manager.shared_variables.init_event.set()
#         #     self.sensodrive_communication_process.start()
#         #     self.counter = 0
#         # self._hardware_input_tab.btn_on.setEnabled(True)
#         # self.lbl_state_update()
#
#     @property
#     def get_hardware_input_list_key(self):
#         return self.hardware_input_list_key
#
#     def state_change_listener(self):
#         self.lbl_state_update()
#
#     def update_shared_variables_from_settings(self):
#         """
#         Updates the settings that are saved internally. NOTE: this is different than with other input modules because
#         we want to be ablte to set friction, damping and spring stiffnes parameters without closing the dialog window.
#         :return:
#         """
#         self.sensodrive_communication_values.endstops = self.settings.endstops
#         self.sensodrive_communication_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
#         self.sensodrive_communication_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
#
#         self.sensodrive_communication_values.friction = self.settings.friction
#         self.sensodrive_communication_values.damping = self.settings.damping
#         self.sensodrive_communication_values.spring_stiffness = self.settings.spring_stiffness
#
#         self.module_manager.shared_variables.update_shared_variables_from_settings_event.set()
#
#
#     def initialize(self):
#         """
#         Just updates the already initialized sensodrive.
#         :return:
#         """
#         self.lbl_state_update()
#
#     def _open_settings_dialog_from_button(self):
#         """
#         Opens and shows the settings dialog from the button on the tab
#         :return:
#         """
#         self._open_settings_dialog()
#         if self.settings_dialog:
#             self.settings_dialog.show()
#
#     def _open_settings_dialog(self):
#         """
#         Not used for this input
#         """
#         self.settings_dialog = SensoDriveSettingsDialog(self.settings)
#         self.settings_dialog.btn_apply.clicked.connect(self.update_shared_variables_from_settings)
#
#     def remove_hardware_input(self):
#         """
#         Removes the sensodrive from the widget and settings
#         NOTE: calls 'self.remove_tab' which is a function of the BaseInput class, if you do_while_running not do_while_running this the tab will not
#         actually disappear from the module.
#         :return:
#         """
#         self.module_manager.shared_variables.close_event.set()
#         while self.module_manager.shared_variables.close_event.is_set():
#             pass
#         self.sensodrive_communication_process.terminate()
#
#         self.module_manager.remove_hardware_input_device(self)
#
#     def disable_remove_button(self):
#         """
#         Disables the sensodrive Remove button, (useful for example when you dont want to be able to remove an input when the
#         simulator is running)
#         :return:
#         """
#         if self._hardware_input_tab.btn_remove_hardware.isEnabled():
#             self._hardware_input_tab.btn_remove_hardware.setEnabled(False)
#
#     def enable_remove_button(self):
#         """
#         Enables the sensodrive remove button.
#         :return:
#         """
#         if not self._hardware_input_tab.btn_remove_hardware.isEnabled():
#             self._hardware_input_tab.btn_remove_hardware.setEnabled(True)
#
#     def lbl_state_update(self):
#         if self.sensodrive_communication_values.sensodrive_motorstate == 0x10:
#             self._hardware_input_tab.lbl_sensodrive_state.setStyleSheet("background-color: orange")
#             self._hardware_input_tab.lbl_sensodrive_state.setText('Off')
#             self._hardware_input_tab.btn_on.setEnabled(True)
#             self._hardware_input_tab.btn_off.setEnabled(False)
#             self._hardware_input_tab.btn_clear_error.setEnabled(False)
#         elif self.sensodrive_communication_values.sensodrive_motorstate == 0x14:
#             self._hardware_input_tab.lbl_sensodrive_state.setStyleSheet("background-color: lightgreen")
#             self._hardware_input_tab.lbl_sensodrive_state.setText('On')
#             self._hardware_input_tab.btn_on.setEnabled(False)
#             self._hardware_input_tab.btn_off.setEnabled(True)
#             self._hardware_input_tab.btn_clear_error.setEnabled(False)
#         elif self.sensodrive_communication_values.sensodrive_motorstate == 0x18:
#             self._hardware_input_tab.lbl_sensodrive_state.setStyleSheet("background-color: red")
#             self._hardware_input_tab.lbl_sensodrive_state.setText('Error')
#             self._hardware_input_tab.btn_on.setEnabled(False)
#             self._hardware_input_tab.btn_off.setEnabled(False)
#             self._hardware_input_tab.btn_clear_error.setEnabled(True)
#         self._hardware_input_tab.repaint()
#
#     def turn_motor_sensodrive_on(self):
#         self.module_manager.shared_variables.turn_on_event.set()
#         time.sleep(0.05)
#         self.lbl_state_update()
#
#     def turn_motor_sensodrive_off(self):
#         self.module_manager.shared_variables.turn_off_event.set()
#         time.sleep(0.05)
#         self.lbl_state_update()
#
#
#     def clear_error(self):
#         self.module_manager.shared_variables.clear_error_event.set()
#         time.sleep(0.05)
#         self.lbl_state_update()
#
#
#     def do_while_running(self):
#         """
#         Basically acts as a portal of variables to the seperate sensodrive communication core. You can send info to this
#         core using the shared variables in 'SensoDriveSharedValues' Class. NOTE THAT YOU SHOULD ONLY SET VARIABLES
#         ON 1 SIDE!! Do not overwrite variables, if you want to send signals for events to the seperate core please use
#         the multiprocessing.Events structure.
#         :return: self._data a dictionary containing :
#             self._data['steering_angle'] = self.sensodrive_communication_values.steering_angle
#             self._data['brake'] = self.sensodrive_communication_values.brake
#             self._data['throttle'] = self.sensodrive_communication_values.throttle
#             self._data['Handbrake'] = 0
#             self._data['Reverse'] = 0
#             self._data['requested_torque'] = requested_torque_by_controller
#             self._data['checked_torque'] = self.safety_checked_torque
#             self._data['torque_rate'] = self.torque_rate
#         """
#
#         # check whether we have a sw_controller that should be updated
#         self._steering_wheel_control_data = self.module_manager.read_news(JOANModules.STEERING_WHEEL_CONTROL)
#         self._carla_interface_data = self.module_manager.read_news(JOANModules.CARLA_INTERFACE)
#
#         self.lbl_state_update()
#
#         try:
#             requested_torque_by_controller = self._steering_wheel_control_data[
#                 self._carla_interface_data['ego_agents']['EgoVehicle 1']['vehicle_object'].selected_sw_controller]['sw_torque']
#         except:
#             requested_torque_by_controller = 0
#
#         self.counter = self.counter + 1
#
#         if self.counter == 5:
#             [self.safety_checked_torque, self.torque_rate] = self.torque_check(
#                 requested_torque=requested_torque_by_controller, t1=self.t1, torque_limit_mnm=20000,
#                 torque_rate_limit_nms=150)
#             self.t1 = int(round(time.time() * 1000))
#             self.counter = 0
#
#         # Write away torque parameters and torque checks
#         self._data['requested_torque'] = requested_torque_by_controller
#         self._data['checked_torque'] = self.safety_checked_torque
#         self._data['torque_rate'] = self.torque_rate
#         self._data['measured_torque'] = self.sensodrive_communication_values.measured_torque
#
#         # Handle all shared parameters with the seperate sensodrive communication core
#         # Get parameters
#         self._data['steering_angle'] = self.sensodrive_communication_values.steering_angle
#         self._data['steering_rate'] = self.sensodrive_communication_values.steering_rate
#         self._data['brake'] = self.sensodrive_communication_values.brake
#         self._data['throttle'] = self.sensodrive_communication_values.throttle
#         self._data['Handbrake'] = 0
#         self._data['Reverse'] = 0
#
#         # print(extra_endstop)
#         #print('req:= ', requested_torque_by_controller, 'safe = ', self.safety_checked_torque)
#         self.sensodrive_communication_values.torque = self.safety_checked_torque
#         self.sensodrive_communication_values.friction = self.settings.friction
#         self.sensodrive_communication_values.damping = self.settings.damping
#
#         self.sensodrive_communication_values.endstops = self.settings.endstops
#         self.sensodrive_communication_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
#         self.sensodrive_communication_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
#         self.sensodrive_communication_values.spring_stiffness = self.settings.spring_stiffness
#
#         # Lastly we also need to write the spring stiffness in data for controller purposes
#         self._data['spring_stiffness'] = self.sensodrive_communication_values.spring_stiffness
#
#         return self._data
#
#     def torque_check(self, requested_torque, t1, torque_rate_limit_nms, torque_limit_mnm):
#         """
#         Checks the torque in 2 ways, one the max capped torque
#         And the torque rate.
#         If the max torque is too high it will cap, if the torque_rate is too high the motor will shut off
#         """
#         t2 = int(round(time.time() * 1000))
#
#         torque_rate = (self.old_requested_torque - requested_torque) / ((t2 - t1) * 1000) * 1000  # Nm/s
#
#         if abs(torque_rate) > torque_rate_limit_nms:
#             print('TORQUE RATE TOO HIGH! TURNING OFF SENSODRIVE')
#             self.shut_off_sensodrive()
#
#         if requested_torque > torque_limit_mnm:
#             checked_torque = torque_limit_mnm
#         elif requested_torque < -torque_limit_mnm:
#             checked_torque = -torque_limit_mnm
#         else:
#             checked_torque = requested_torque
#
#         # update torque for torque rate calc
#         self.old_requested_torque = requested_torque
#
#         return [checked_torque, torque_rate]

class JOANSensoDriveMP:
    def __init__(self, settings, shared_variables):
        self.settings = settings

        self.settings_dialog = None
        self.shared_variables = shared_variables

class SensoDriveComm(mp.Process):
    def __init__(self, shared_variables, init_event, turn_on_event, turn_off_event, clear_error_event, close_event, update_event):
        super().__init__()
        self.init_event = init_event
        self.turn_on_event = turn_on_event
        self.close_event = close_event
        self.update_settings_event = update_event
        self.turn_off_event = turn_off_event
        self.clear_error_event = clear_error_event

        # Create PCAN object
        self.pcan_object = None
        self.pcan_initialization_result = None

        # shared values class to exchange data between this process and others
        self.sensodrive_communication_values = shared_variables

        # if connecting more Sensowheels, different USB/PCAN bus
        if self.sensodrive_communication_values.sensodrive_ID == 0:
            self._pcan_channel = PCAN_USBBUS1
        elif self.sensodrive_communication_values.sensodrive_ID == 1:
            self._pcan_channel = PCAN_USBBUS2

        # Create steering wheel parameters data structure
        self.steering_wheel_parameters = {}

        # Initialize message structures
        self.steering_wheel_message = TPCANMsg()
        self.state_message = TPCANMsg()
        self.pedal_message = TPCANMsg()
        self.sensodrive_initialization_message = TPCANMsg()
        self.state_change_message = TPCANMsg()

        self.state_change_message.ID = INITIALIZATION_MESSAGE_ID
        self.state_change_message.LEN = INITIALIZATION_MESSAGE_LENGTH
        self.state_change_message.TYPE = PCAN_MESSAGE_STANDARD
        # mode of operation
        self.state_change_message.DATA[0] = 0x11
        self.state_change_message.DATA[1] = 0x00
        # End stop position
        self.state_change_message.DATA[2] = 0xB4
        self.state_change_message.DATA[3] = 0x00
        # Torque beyond end stops:
        self.state_change_message.DATA[6] = 0x14
        self.state_change_message.DATA[7] = 0x14

        self._current_state_hex = 0x00

    def initialize(self):
        self.pcan_object = PCANBasic()
        if self.pcan_initialization_result is None:
            self.pcan_initialization_result = self.pcan_object.Initialize(self._pcan_channel, PCAN_BAUD_1M)

        # Convert our shared settings to bytes
        endstops_bytes = int.to_bytes(int(math.degrees(self.sensodrive_communication_values.endstops)), 2, byteorder='little', signed=True)
        torque_limit_between_endstops_bytes = int.to_bytes(self.sensodrive_communication_values.torque_limit_between_endstops, 1, byteorder='little', signed=False)
        torque_limit_beyond_endstops_bytes = int.to_bytes(self.sensodrive_communication_values.torque_limit_beyond_endstops, 1, byteorder='little', signed=False)

        # We need to have our init message here as well
        self.sensodrive_initialization_message.ID = INITIALIZATION_MESSAGE_ID
        self.sensodrive_initialization_message.LEN = INITIALIZATION_MESSAGE_LENGTH
        self.sensodrive_initialization_message.TYPE = PCAN_MESSAGE_STANDARD
        # mode of operation
        self.sensodrive_initialization_message.DATA[0] = 0x11
        # reserved
        self.sensodrive_initialization_message.DATA[1] = 0
        # Endstop position
        self.sensodrive_initialization_message.DATA[2] = endstops_bytes[0]
        self.sensodrive_initialization_message.DATA[3] = endstops_bytes[1]
        # reserved
        self.sensodrive_initialization_message.DATA[4] = 0
        self.sensodrive_initialization_message.DATA[5] = 0
        # Torque between endstops:
        self.sensodrive_initialization_message.DATA[6] = torque_limit_between_endstops_bytes[0]
        # Torque beyond endstops:
        self.sensodrive_initialization_message.DATA[7] = torque_limit_beyond_endstops_bytes[0]

        self.pcan_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.002)
        self.pcan_object.Read(self._pcan_channel)

        # do_while_running not switch mode
        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

        # Set the data structure for the steeringwheel message with the just applied values
        self.steering_wheel_parameters = self._map_si_to_sensodrive(self.sensodrive_communication_values)

        # TODO Do we need to do_while_running this twice?
        self.pcan_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.02)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]

        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11
        print(hex(self._current_state_hex))
        self.sensodrive_communication_values.sensodrive_motorstate = self._current_state_hex

        # self._current_state_hex = 0x00

    def update_settings(self):
        endstops_bytes = int.to_bytes(int(math.degrees(self.sensodrive_communication_values.endstops)), 2, byteorder='little', signed=True)
        torque_limit_between_endstops_bytes = int.to_bytes(self.sensodrive_communication_values.torque_limit_between_endstops, 1, byteorder='little', signed=False)
        torque_limit_beyond_endstops_bytes = int.to_bytes(self.sensodrive_communication_values.torque_limit_beyond_endstops, 1, byteorder='little', signed=False)

        # We need to have our init message here as well
        self.sensodrive_initialization_message.ID = INITIALIZATION_MESSAGE_ID
        self.sensodrive_initialization_message.LEN = INITIALIZATION_MESSAGE_LENGTH
        self.sensodrive_initialization_message.TYPE = PCAN_MESSAGE_STANDARD
        # mode of operation
        self.sensodrive_initialization_message.DATA[0] = 0x11
        # reserved
        self.sensodrive_initialization_message.DATA[1] = 0
        # Endstop position
        self.sensodrive_initialization_message.DATA[2] = endstops_bytes[0]
        self.sensodrive_initialization_message.DATA[3] = endstops_bytes[1]
        # reserved
        self.sensodrive_initialization_message.DATA[4] = 0
        self.sensodrive_initialization_message.DATA[5] = 0
        # Torque between endstops:
        self.sensodrive_initialization_message.DATA[6] = torque_limit_between_endstops_bytes[0]
        # Torque beyond endstops:
        self.sensodrive_initialization_message.DATA[7] = torque_limit_beyond_endstops_bytes[0]

        self.pcan_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.002)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]
        self.sensodrive_communication_values.sensodrive_motorstate = self._current_state_hex
    def _map_si_to_sensodrive(self, shared_variables):
        # convert SI units to Sensowheel units

        out = {
            'torque': int(shared_variables.torque * 1000.0),
            'friction': int(shared_variables.friction * 1000.0),
            'damping': int(shared_variables.damping * 1000.0 * (2.0 * math.pi) / 60.0),
            'spring_stiffness': int(shared_variables.spring_stiffness * 1000.0 / (180.0 / math.pi))
        }

        return out

    def _sensodrive_data_to_si(self, received):
        if received[1].ID == STEERINGWHEEL_MESSAGE_RECEIVE_ID:
            # steering wheel

            # steering angle
            increments = int.from_bytes(received[1].DATA[0:4], byteorder='little', signed=True)
            self.sensodrive_communication_values.steering_angle = math.radians(float(increments) * 0.009)  # we get increments, convert to deg, convert to rad

            # steering rate
            steering_rate = int.from_bytes(received[1].DATA[4:6], byteorder='little', signed=True)
            self.sensodrive_communication_values.steering_rate = float(steering_rate) * (2.0 * math.pi) / 60.0  # we get rev/min, convert to rad/s

            # torque
            torque = int.from_bytes(received[1].DATA[6:], byteorder='little', signed=True)
            self.sensodrive_communication_values.measured_torque = float(torque) / 1000.0  # we get mNm convert to Nm

        elif received[1].ID == PEDAL_MESSAGE_RECEIVE_ID:
            # pedals
            self.sensodrive_communication_values.throttle = float(int.from_bytes(received[1].DATA[2:4], byteorder='little') - 1100) / 2460.0
            self.sensodrive_communication_values.brake = float(int.from_bytes(received[1].DATA[4:6], byteorder='little') - 1) / 500

        elif received[1].ID == STATE_MESSAGE_RECEIVE_ID:
            #
            self._current_state_hex = received[1].DATA[0]

    def run(self):
        self.init_event.wait()
        self.initialize()

        while True:
            # Turn off SensoDrive immediately (only when torque limits are breached)
            if self.turn_off_event.is_set():
                self.on_to_off(self.state_message)
                self.turn_off_event.clear()

            # Get latest parameters
            time.sleep(0.00001)

            # convert SI units to Sensowheel units
            self.steering_wheel_parameters = self._map_si_to_sensodrive(self.sensodrive_communication_values)

            # send steering wheel data
            self.write_message_steering_wheel(self.pcan_object, self.steering_wheel_message, self.steering_wheel_parameters)

            # receive data from Sensodrive (wheel, pedals)
            received = self.pcan_object.Read(self._pcan_channel)

            # request state data
            endstops_bytes = int.to_bytes(int(math.degrees(self.sensodrive_communication_values.endstops)), 2, byteorder='little', signed=True)
            self.state_message.DATA[2] = endstops_bytes[0]
            self.state_message.DATA[3] = endstops_bytes[1]

            self.pcan_object.Write(self._pcan_channel, self.state_message)
            received2 = self.pcan_object.Read(self._pcan_channel)

            # request pedal data
            self.write_message_pedals(self.pcan_object, self.pedal_message)
            received3 = self.pcan_object.Read(self._pcan_channel)

            if received[0] or received2[0] or received3[0] == PCAN_ERROR_OK:
                self._sensodrive_data_to_si(received)

                self._sensodrive_data_to_si(received2)

                self._sensodrive_data_to_si(received3)

            self.sensodrive_communication_values.sensodrive_motorstate = self._current_state_hex

            if self.turn_on_event.is_set():
                self.off_to_on(self.state_message)
                self.turn_on_event.clear()

            if self.clear_error_event.is_set():
                self.clear_error(self.state_message)
                self.clear_error_event.clear()

            if self.update_settings_event.is_set():
                self.update_settings()
                self.update_settings_event.clear()

            # properly uninitialize the pcan dongle if sensodrive is removed
            if self.close_event.is_set():
                self.close_event.clear()
                print('Uninitialized pcan_object')
                self.pcan_object.Uninitialize(self._pcan_channel)
                break

            pass

    def write_message_steering_wheel(self, pcan_object, pcanmessage, data):
        """
        Writes a CAN message to the sensodrive containing information regarding torque, friction and damping. Also
        returns the current state of the wheel (angle, force etc).
        :param pcan_object:
        :param pcanmessage:
        :param data:
        :return:
        """
        torque_bytes = int.to_bytes(data['torque'], 2, byteorder='little', signed=True)
        friction_bytes = int.to_bytes(data['friction'], 2, byteorder='little', signed=True)
        damping_bytes = int.to_bytes(data['damping'], 2, byteorder='little', signed=True)
        spring_stiffness_bytes = int.to_bytes(data['spring_stiffness'], 2, byteorder='little', signed=True)

        pcanmessage.ID = STEERINGWHEEL_MESSAGE_SEND_ID
        pcanmessage.LEN = STEERINGWHEEL_MESSAGE_LENGTH
        pcanmessage.TYPE = PCAN_MESSAGE_STANDARD
        pcanmessage.DATA[0] = torque_bytes[0]
        pcanmessage.DATA[1] = torque_bytes[1]
        pcanmessage.DATA[2] = friction_bytes[0]
        pcanmessage.DATA[3] = friction_bytes[1]
        pcanmessage.DATA[4] = damping_bytes[0]
        pcanmessage.DATA[5] = damping_bytes[1]
        pcanmessage.DATA[6] = spring_stiffness_bytes[0]
        pcanmessage.DATA[7] = spring_stiffness_bytes[1]

        pcan_object.Write(self._pcan_channel, pcanmessage)

    def write_message_pedals(self, pcan_object, pcanmessage):
        """
        Writes a correctly structured CAN message to the sensodrive which will return a message containing the
        inputs of the pedals.
        :param pcan_object:
        :param pcanmessage:
        :return:
        """
        pcanmessage.ID = 0x20C
        pcanmessage.LEN = 1
        pcanmessage.MSGTYPE = PCAN_MESSAGE_STANDARD

        pcanmessage.DATA[0] = 0x1

        pcan_object.Write(self._pcan_channel, pcanmessage)

    def off_to_on(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from off to on.
        :return:
        """
        print('off to on')
        message.DATA[0] = 0x10
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.002)

        message.DATA[0] = 0x12
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.002)

        message.DATA[0] = 0x14
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.002)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]
        # print(hex(self._current_state_hex))
        time.sleep(0.002)
        self.sensodrive_communication_values.sensodrive_motorstate = self._current_state_hex




    def on_to_off(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from on to off.
        :return:
        """
        print('on to off')
        message.DATA[0] = 0x12
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.002)
        message.DATA[0] = 0x10
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.002)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]
        # print(hex(self._current_state_hex))
        time.sleep(0.002)
        self.sensodrive_communication_values.sensodrive_motorstate = self._current_state_hex

    def clear_error(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from error to off.
        :return:
        """
        print('clear error')
        message.DATA[0] = 0x1F
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.002)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]
        print(hex(self._current_state_hex))
        time.sleep(0.002)
        self.sensodrive_communication_values.sensodrive_motorstate = self._current_state_hex

class SensoDriveCommunicationValues:
    """"
    This class contains all the variables that are shared between the seperate hardware communication core and the
    main JOAN core.
    """

    def __init__(self):
        # Encoder Values
        self._steering_angle = mp.Value(c_float, 0.0)             # [rad]
        self._throttle = mp.Value(c_float, 0.0)                   # [-] 0 - 1
        self._brake = mp.Value(c_float, 0.0)                      # [-] 0 - 1

        self._steering_rate = mp.Value(c_float, 0.0)          # [rad/s]

        # Steering Parameter Values
        self._friction = mp.Value(c_float, 0.0)                     # [Nm]
        self._damping = mp.Value(c_float, 0.0)                      # [Nm s / rad]
        self._spring_stiffness = mp.Value(c_float, 0.0)             # [Nm / rad]
        self._torque = mp.Value(c_float, 0.0)                       # [Nm]

        # Extra Info Parameters
        self._measured_torque = mp.Value(c_float, 0.0)              # [Nm]
        self._sensodrive_motorstate = mp.Value(c_int, 0)        # [-]

        # SensoDrive Settings (torque limits, endstops etc)
        self._endstops = mp.Value(c_float, 0.0)                     # [rad]
        self._torque_limit_between_endstops = mp.Value(c_int, 0) # [%]
        self._torque_limit_beyond_endstops = mp.Value(c_int, 0)  # [%]

        # SensoDrive (ID) or number of sensodrives
        self._sensodrive_ID = mp.Value(c_int, 0)                # [-]

    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, var):
        self._steering_angle.value = var

    @property
    def steering_rate(self):
        return self._steering_rate.value

    @steering_rate.setter
    def steering_rate(self, var):
        self._steering_rate.value = var

    @property
    def throttle(self):
        return self._throttle.value

    @throttle.setter
    def throttle(self, var):
        self._throttle.value = var

    @property
    def brake(self):
        return self._brake.value

    @brake.setter
    def brake(self, var):
        self._brake.value = var

    @property
    def friction(self):
        return self._friction.value

    @friction.setter
    def friction(self, var):
        self._friction.value = var

    @property
    def damping(self):
        return self._damping.value

    @damping.setter
    def damping(self, var):
        self._damping.value = var

    @property
    def spring_stiffness(self):
        return self._spring_stiffness.value

    @spring_stiffness.setter
    def spring_stiffness(self, var):
        self._spring_stiffness.value = var

    @property
    def torque(self):
        return self._torque.value

    @torque.setter
    def torque(self, var):
        self._torque.value = var

    @property
    def measured_torque(self):
        return self._measured_torque.value

    @measured_torque.setter
    def measured_torque(self, var):
        self._measured_torque.value = var

    @property
    def endstops(self):
        return self._endstops.value

    @endstops.setter
    def endstops(self, var):
        self._endstops.value = var

    @property
    def torque_limit_between_endstops(self):
        return self._torque_limit_between_endstops.value

    @torque_limit_between_endstops.setter
    def torque_limit_between_endstops(self, var):
        self._torque_limit_between_endstops.value = var

    @property
    def torque_limit_beyond_endstops(self):
        return self._torque_limit_beyond_endstops.value

    @torque_limit_beyond_endstops.setter
    def torque_limit_beyond_endstops(self, var):
        self._torque_limit_beyond_endstops.value = var

    @property
    def sensodrive_motorstate(self):
        return self._sensodrive_motorstate.value

    @sensodrive_motorstate.setter
    def sensodrive_motorstate(self, var):
        self._sensodrive_motorstate.value = var

    @property
    def sensodrive_ID(self):
        return self._sensodrive_ID.value

    @sensodrive_ID.setter
    def sensodrive_ID(self, var):
        self._sensodrive_ID.value = var
