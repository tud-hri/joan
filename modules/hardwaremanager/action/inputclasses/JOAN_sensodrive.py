import os
import time

from PyQt5 import uic, QtWidgets

from modules.hardwaremanager.action.hardwaremanagersettings import SensoDriveSettings
from modules.hardwaremanager.action.inputclasses.PCANBasic import *
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.joanmodules import JOANModules
from process.statesenum import State

import multiprocessing as mp

"""
These global parameters are used to make the message ID's more identifiable than just the hex nr.
"""
INITIALIZATION_MESSAGE_ID = 0x200
INITIALIZATION_MESSAGE_LENGTH = 8

STEERINGWHEEL_MESSAGE_ID = 0x201
STEERINGWHEEL_MESSAGE_LENGTH = 8

PEDAL_MESSAGE_ID = 0x20C
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
        self._display_values()

        self.btn_apply.clicked.connect(self.update_parameters)
        # self.show()

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


class JOAN_SensoDrive(BaseInput):
    """
    Main class for the SensoDrive input, inherits from BaseInput (as it should!)
    """

    def __init__(self, hardware_manager_action, sensodrive_tab, nr_of_sensodrives, settings: SensoDriveSettings):
        """
        Initializes the class, also uses some more parameters to keep track of how many sensodrives are connected
        :param hardware_manager_action:
        :param sensodrive_tab:
        :param nr_of_sensodrives:
        :param settings:
        """
        super().__init__(hardware_manager_action)

        # Create the shared variables class
        self.sensodrive_shared_values = SensoDriveSharedValues()

        # Torque safety variables
        self.counter = 0
        self.old_requested_torque = 0
        self.safety_checked_torque = 0
        self.t1 = 0
        self.torque_rate = 0

        # Set administrative variables
        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self.settings = settings
        self.module_action = hardware_manager_action

        #  hook up buttons
        self._sensodrive_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._sensodrive_tab.btn_settings.clicked.connect(self._open_settings_from_button)
        self._sensodrive_tab.btn_visualization.setEnabled(False)
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)
        self._sensodrive_tab.btn_on_off.clicked.connect(self.toggle_on_off)
        self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: orange")
        self._sensodrive_tab.btn_on_off.setText('Off')
        self._sensodrive_tab.btn_on_off.setEnabled(True)

        self.settings_dialog = SensoDriveSettingsDialog(self.settings)
        self.settings_dialog.accepted.connect(self.update_settings)
        self.settings_dialog.btn_apply.clicked.connect(self.update_settings)

        self.sensodrive_shared_values.torque = self.settings.torque
        self.sensodrive_shared_values.friction = self.settings.friction
        self.sensodrive_shared_values.damping = self.settings.damping
        self.sensodrive_shared_values.spring_stiffness = self.settings.spring_stiffness

        self.sensodrive_shared_values.endstops = self.settings.endstops
        self.sensodrive_shared_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
        self.sensodrive_shared_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops

        self.init_event = mp.Event()
        self.close_event = mp.Event()
        self.toggle_sensodrive_motor_event = mp.Event()
        self.update_settings_event = mp.Event()
        self.sensodrive_communication_process = SensoDriveComm(self.sensodrive_shared_values, self.init_event,
                                                               self.toggle_sensodrive_motor_event, self.close_event,
                                                               self.update_settings_event)

    def update_settings(self):
        """
        Updates the settings that are saved internally. NOTE: this is different than with other input modules because
        we want to be ablte to set friction, damping and spring stiffnes parameters without closing the dialog window.
        :return:
        """
        self.sensodrive_shared_values.endstops = self.settings.endstops
        self.sensodrive_shared_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
        self.sensodrive_shared_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops

        self.sensodrive_shared_values.friction = self.settings.friction
        self.sensodrive_shared_values.damping = self.settings.damping
        self.sensodrive_shared_values.spring_stiffness = self.settings.spring_stiffness
        self.update_settings_event.set()

    def initialize(self):
        """
        Initializes the sensodrive by sending several PCAN messages which will get the sensodrive in the appropriate
        state.
        :return:
        """

        # self.sensodrive_communication_process.initialize()
        self.init_event.set()
        self.sensodrive_communication_process.start()

        self.counter = 0

    def _toggle_on_off(self, connected):
        """
        Toggles the sensodrive actuator on and off by cycling through different PCANmessages
        :param connected:
        :return:
        """
        if connected == False:
            try:
                self.on_to_off()
            except:
                pass

    def _open_settings_from_button(self):
        """
        Opens and shows the settings dialog from the button on the tab
        :return:
        """
        if self.settings_dialog:
            self.settings_dialog.show()

    def _open_settings_dialog(self):
        """
        Not used for this input
        """
        pass

    def remove_func(self):
        """
        Removes the sensodrive from the widget and settings
        NOTE: calls 'self.remove_tab' which is a function of the BaseInput class, if you do not do this the tab will not
        actually disappear from the module.
        :return:
        """
        self.close_event.set()
        time.sleep(0.05)
        self.sensodrive_communication_process.terminate()
        self.module_action.settings.sensodrives.remove(self.settings)
        self.remove_tab(self._sensodrive_tab)

    def disable_remove_button(self):
        """
        Disables the sensodrive Remove button, (useful for example when you dont want to be able to remove an input when the
        simulator is running)
        :return:
        """
        if self._sensodrive_tab.btn_remove_hardware.isEnabled() is True:
            self._sensodrive_tab.btn_remove_hardware.setEnabled(False)
        else:
            pass

    def enable_remove_button(self):
        """
        Enables the sensodrive remove button.
        :return:
        """
        if self._sensodrive_tab.btn_remove_hardware.isEnabled() is False:
            self._sensodrive_tab.btn_remove_hardware.setEnabled(True)
        else:
            pass

    def toggle_on_off(self):
        """
        If a PCAN dongle is connected and working will check what state the sensodrive is in and take the appropriate action
        (0x10 is ready, 0x14 is on and 0x18 is error)
        :return:
        """
        self.toggle_sensodrive_motor_event.set()
        # give the seperate process time to handle the signal
        if self.module_action.state_machine.current_state != State.RUNNING:
            time.sleep(0.02)

        if self.sensodrive_shared_values.sensodrive_motorstate == 0x10:
            self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: orange")
            self._sensodrive_tab.btn_on_off.setText('Off')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x14:
            self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: lightgreen")
            self._sensodrive_tab.btn_on_off.setText('On')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x18:
            self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: red")
            self._sensodrive_tab.btn_on_off.setText('Clear Error')

    def do(self):
        """
        Basically acts as a portal of variables to the seperate sensodrive communication process. You can send info to this
        process using the shared variables in 'SensoDriveSharedValues' Class. NOTE THAT YOU SHOULD ONLY SET VARIABLES
        ON 1 SIDE!! Do not overwrite variables, if you want to send signals for events to the seperate process please use
        the multiprocessing.Events structure.
        :return: self._data a dictionary containing :
            self._data['SteeringInput'] = self.sensodrive_shared_values.steering_angle
            self._data['BrakeInput'] = self.sensodrive_shared_values.brake
            self._data['ThrottleInput'] = self.sensodrive_shared_values.throttle
            self._data['Handbrake'] = 0
            self._data['Reverse'] = 0
            self._data['requested_torque'] = requested_torque_by_controller
            self._data['checked_torque'] = self.safety_checked_torque
            self._data['torque_rate'] = self.torque_rate
        """
        # check on the motordrive status and change button appearance
        if self.sensodrive_shared_values.sensodrive_motorstate == 0x10:
            self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: orange")
            self._sensodrive_tab.btn_on_off.setText('Off')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x14:
            self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: lightgreen")
            self._sensodrive_tab.btn_on_off.setText('On')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x18:
            self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: red")
            self._sensodrive_tab.btn_on_off.setText('Clear Error')

        # check whether we have a sw_controller that should be updated
        self._steering_wheel_control_data = self._action.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        self._carla_interface_data = self._action.read_news(JOANModules.CARLA_INTERFACE)

        try:
            requested_torque_by_controller = self._steering_wheel_control_data[
                self._carla_interface_data['ego_agents']['Car 1']['vehicle_object'].selected_sw_controller]['sw_torque']
        except:
            requested_torque_by_controller = 0

        self.counter = self.counter + 1

        if self.counter == 5:
            [self.safety_checked_torque, self.torque_rate] = self.torque_check(
                requested_torque=requested_torque_by_controller, t1=self.t1, torque_limit_mNm=5000,
                torque_rate_limit_Nms=20)
            self.t1 = int(round(time.time() * 1000))
            self.counter = 0

        # Write away torque parameters and torque checks
        self._data['requested_torque'] = requested_torque_by_controller
        self._data['checked_torque'] = self.safety_checked_torque
        self._data['torque_rate'] = self.torque_rate
        self._data['measured_torque'] = self.sensodrive_shared_values.measured_torque

        # Handle all shared parameters with the seperate sensodrive communication process
        # Get parameters
        self._data['SteeringInput'] = self.sensodrive_shared_values.steering_angle
        self._data['BrakeInput'] = self.sensodrive_shared_values.brake
        self._data['ThrottleInput'] = self.sensodrive_shared_values.throttle
        print(self._data['ThrottleInput'], self._data['BrakeInput'])
        self._data['Handbrake'] = 0
        self._data['Reverse'] = 0

        # Set parameters
        self.sensodrive_shared_values.torque = self.safety_checked_torque
        self.sensodrive_shared_values.friction = self.settings.friction
        self.sensodrive_shared_values.damping = self.settings.damping
        self.sensodrive_shared_values.endstops = self.settings.endstops
        self.sensodrive_shared_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
        self.sensodrive_shared_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
        self.sensodrive_shared_values.spring_stiffness = self.settings.spring_stiffness

        # Lastly we also need to write the spring stiffness in data for controller purposes
        self._data['spring_stiffness'] = self.sensodrive_shared_values.spring_stiffness

        return self._data

    def torque_check(self, requested_torque, t1, torque_rate_limit_Nms, torque_limit_mNm):
        """
        Checks the torque in 2 ways, one the max capped torque
        And the torque rate.
        If the max torque is too high it will cap, if the torque_rate is too high the motor will shut off
        """
        t2 = int(round(time.time() * 1000))

        torque_rate = (self.old_requested_torque - requested_torque) / ((t2 - t1) * 1000) * 1000  # Nm/s

        if (abs(torque_rate) > torque_rate_limit_Nms):
            print('TORQUE RATE TOO HIGH! TURNING OFF SENSODRIVE')
            self.toggle_on_off()

        if requested_torque > torque_limit_mNm:
            checked_torque = torque_limit_mNm
        elif requested_torque < -torque_limit_mNm:
            checked_torque = -torque_limit_mNm
        else:
            checked_torque = requested_torque

        # update torque for torque rate calc
        self.old_requested_torque = requested_torque

        return [checked_torque, torque_rate]


class SensoDriveSharedValues:
    """"
    This class contains all the variables that are shared between the seperate hardware communication process and the
    main JOAN process.
    """

    def __init__(self):
        # Encoder Values
        self._steering_angle = mp.Value(c_float, 0)
        self._throttle = mp.Value(c_float, 0)
        self._brake = mp.Value(c_float, 0)

        # Steering Parameter Values
        self._friction = mp.Value(c_int, 0)
        self._damping = mp.Value(c_int, 0)
        self._spring_stiffness = mp.Value(c_int, 0)
        self._torque = mp.Value(c_int, 0)

        # Extra Info Parameters
        self._measured_torque = mp.Value(c_int, 0)
        self._sensodrive_motorstate = mp.Value(c_int, 0)

        # SensoDrive Settings (torque limits, endstops etc)
        self._endstops = mp.Value(c_int, 0)
        self._torque_limit_between_endstops = mp.Value(c_int, 0)
        self._torque_limit_beyond_endstops = mp.Value(c_int, 0)

    @property
    def steering_angle(self):
        return self._steering_angle.value

    @steering_angle.setter
    def steering_angle(self, var):
        self._steering_angle.value = var

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


class SensoDriveComm(mp.Process):
    def __init__(self, shared_values, init_event, toggle_event, close_event, update_event):
        super().__init__()
        self.init_event = init_event
        self.toggle_sensodrive_motor_event = toggle_event
        self.close_event = close_event
        self.update_settings_event = update_event

        # Create PCAN object
        self.pcan_initialization_result = None
        self.sensodrive_shared_values = shared_values
        self._pcan_channel = PCAN_USBBUS1

        # Create steeringwheel parameters data structure
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
        # Endstop position
        self.state_change_message.DATA[2] = 0xB4
        self.state_change_message.DATA[3] = 0x00
        # Torque beyond endstops:
        self.state_change_message.DATA[6] = 0x14
        self.state_change_message.DATA[7] = 0x14

        self._current_state_hex = 0x00

    def initialize(self):
        self.PCAN_object = PCANBasic()
        if self.pcan_initialization_result is None:
            self.pcan_initialization_result = self.PCAN_object.Initialize(
                self._pcan_channel, PCAN_BAUD_1M)

        # Convert our shared settings to bytes

        self.endstops_bytes = int.to_bytes(self.sensodrive_shared_values.endstops, 2, byteorder='little', signed=True)
        self.torque_limit_between_endstops_bytes = int.to_bytes(
            self.sensodrive_shared_values.torque_limit_between_endstops, 1, byteorder='little', signed=False)
        self.torque_limit_beyond_endstops_bytes = int.to_bytes(
            self.sensodrive_shared_values.torque_limit_beyond_endstops, 1, byteorder='little', signed=False)

        # We need to have our init message here as well
        self.sensodrive_initialization_message.ID = INITIALIZATION_MESSAGE_ID
        self.sensodrive_initialization_message.LEN = INITIALIZATION_MESSAGE_LENGTH
        self.sensodrive_initialization_message.TYPE = PCAN_MESSAGE_STANDARD
        # mode of operation
        self.sensodrive_initialization_message.DATA[0] = 0x11
        # reserved
        self.sensodrive_initialization_message.DATA[1] = 0
        # Endstop position
        self.sensodrive_initialization_message.DATA[2] = self.endstops_bytes[0]
        self.sensodrive_initialization_message.DATA[3] = self.endstops_bytes[1]
        # reserved
        self.sensodrive_initialization_message.DATA[4] = 0
        self.sensodrive_initialization_message.DATA[5] = 0
        # Torque between endstops:
        self.sensodrive_initialization_message.DATA[6] = self.torque_limit_between_endstops_bytes[0]
        # Torque beyond endstops:
        self.sensodrive_initialization_message.DATA[7] = self.torque_limit_beyond_endstops_bytes[0]

        self.PCAN_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.02)
        self.response = self.PCAN_object.Read(self._pcan_channel)

        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

        # Set the data structure for the steeringwheel message with the just applied values
        self.steering_wheel_parameters['torque'] = 0  # (You dont want to start to turn the wheel at startup)
        self.steering_wheel_parameters['friction'] = self.sensodrive_shared_values.friction
        self.steering_wheel_parameters['damping'] = self.sensodrive_shared_values.damping
        self.steering_wheel_parameters['spring_stiffness'] = self.sensodrive_shared_values.spring_stiffness
        print('initializing SensoDrive')

        self.PCAN_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.02)
        response = self.PCAN_object.Read(self._pcan_channel)
        #
        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

        self._current_state_hex = 0x00

    def update_settings(self):
        self.endstops_bytes = int.to_bytes(self.sensodrive_shared_values.endstops, 2, byteorder='little', signed=True)
        self.torque_limit_between_endstops_bytes = int.to_bytes(
            self.sensodrive_shared_values.torque_limit_between_endstops, 1, byteorder='little', signed=False)
        self.torque_limit_beyond_endstops_bytes = int.to_bytes(
            self.sensodrive_shared_values.torque_limit_beyond_endstops, 1, byteorder='little', signed=False)

        # We need to have our init message here as well
        self.sensodrive_initialization_message.ID = INITIALIZATION_MESSAGE_ID
        self.sensodrive_initialization_message.LEN = INITIALIZATION_MESSAGE_LENGTH
        self.sensodrive_initialization_message.TYPE = PCAN_MESSAGE_STANDARD
        # mode of operation
        self.sensodrive_initialization_message.DATA[0] = 0x11
        # reserved
        self.sensodrive_initialization_message.DATA[1] = 0
        # Endstop position
        self.sensodrive_initialization_message.DATA[2] = self.endstops_bytes[0]
        self.sensodrive_initialization_message.DATA[3] = self.endstops_bytes[1]
        # reserved
        self.sensodrive_initialization_message.DATA[4] = 0
        self.sensodrive_initialization_message.DATA[5] = 0
        # Torque between endstops:
        self.sensodrive_initialization_message.DATA[6] = self.torque_limit_between_endstops_bytes[0]
        # Torque beyond endstops:
        self.sensodrive_initialization_message.DATA[7] = self.torque_limit_beyond_endstops_bytes[0]

        self.PCAN_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.02)
        self.response = self.PCAN_object.Read(self._pcan_channel)

    def run(self):
        self.init_event.wait()
        self.initialize()

        while True:
            # Get latest parameters
            time.sleep(0.001)
            self.steering_wheel_parameters['torque'] = self.sensodrive_shared_values.torque
            self.steering_wheel_parameters['friction'] = self.sensodrive_shared_values.friction
            self.steering_wheel_parameters['damping'] = self.sensodrive_shared_values.damping
            self.steering_wheel_parameters['spring_stiffness'] = self.sensodrive_shared_values.spring_stiffness

            # request and set steering wheel data
            self.write_message_steering_wheel(self.PCAN_object, self.steering_wheel_message,
                                              self.steering_wheel_parameters)
            received = self.PCAN_object.Read(self._pcan_channel)

            # request state data
            self.PCAN_object.Write(self._pcan_channel, self.state_message)
            received2 = self.PCAN_object.Read(self._pcan_channel)

            # request pedal data
            self.write_message_pedals(self.PCAN_object, self.pedal_message)
            received3 = self.PCAN_object.Read(self._pcan_channel)

            if (received[0] or received2[0] or received3[0] == PCAN_ERROR_OK):
                if (received[1].ID == 0x211):
                    Increments = int.from_bytes(received[1].DATA[0:4], byteorder='little', signed=True)
                    Angle = round(Increments * 0.009, 4)
                    # Steering:
                    self.sensodrive_shared_values.steering_angle = Angle
                    # Torque
                    Torque = int.from_bytes(received[1].DATA[6:], byteorder='little', signed=True)
                    self.sensodrive_shared_values.torque_measured = Torque
                elif (received[1].ID == 0x210):
                    self._current_state_hex = received[1].DATA[0]
                elif (received[1].ID == 0x21C):
                    self.sensodrive_shared_values.throttle = (int.from_bytes(received[1].DATA[2:4],
                                                                             byteorder='little') - 1100) / 2460 * 100
                    self.sensodrive_shared_values.brake = (int.from_bytes(received[1].DATA[4:6],
                                                                          byteorder='little') - 1) / 500 * 100

                if (received2[1].ID == 0x211):
                    Increments = int.from_bytes(received2[1].DATA[0:4], byteorder='little', signed=True)
                    Angle = round(Increments * 0.009, 4)
                    # Steering:
                    self.sensodrive_shared_values.steering_angle = Angle
                    # Torque
                    Torque = int.from_bytes(received2[1].DATA[6:], byteorder='little', signed=True)
                    self.sensodrive_shared_values.torque_measured = Torque
                elif (received2[1].ID == 0x210):
                    self._current_state_hex = received2[1].DATA[0]
                elif (received2[1].ID == 0x21C):
                    self.sensodrive_shared_values.throttle = (int.from_bytes(received2[1].DATA[2:4],
                                                                             byteorder='little') - 1100) / 2460 * 100
                    self.sensodrive_shared_values.brake = (int.from_bytes(received2[1].DATA[4:6],
                                                                          byteorder='little') - 1) / 500 * 100

                if (received3[1].ID == 0x211):
                    Increments = int.from_bytes(received3[1].DATA[0:4], byteorder='little', signed=True)
                    Angle = round(Increments * 0.009, 4)
                    # Steering:
                    self.sensodrive_shared_values.steering_angle = Angle
                    # Torque
                    Torque = int.from_bytes(received3[1].DATA[6:], byteorder='little', signed=True)
                    self.sensodrive_shared_values.torque_measured = Torque
                elif (received3[1].ID == 0x210):
                    self._current_state_hex = received3[1].DATA[0]
                elif (received3[1].ID == 0x21C):
                    self.sensodrive_shared_values.throttle = (int.from_bytes(received3[1].DATA[2:4],
                                                                             byteorder='little') - 1100) / 2460 * 100
                    self.sensodrive_shared_values.brake = (int.from_bytes(received3[1].DATA[4:6],
                                                                          byteorder='little') - 1) / 500 * 100

            self.sensodrive_shared_values.sensodrive_motorstate = self._current_state_hex

            if self.toggle_sensodrive_motor_event.is_set():
                self.on_off()
                self.toggle_sensodrive_motor_event.clear()

            if self.update_settings_event.is_set():
                self.update_settings()
                self.update_settings_event.clear()

            # properly uninitialize the pcan dongle if sensodrive is removed
            if self.close_event.is_set():
                self.close_event.clear()
                print('uninitialized pcan_object')
                self.PCAN_object.Uninitialize(self._pcan_channel)
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

        pcanmessage.ID = STEERINGWHEEL_MESSAGE_ID
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

    def on_off(self):
        """
        If a PCAN dongle is connected and working will check what state the sensodrive is in and take the appropriate action
        (0x10 is ready, 0x14 is on and 0x18 is error)
        :return:
        """
        if (self._current_state_hex == 0x10):
            self.off_to_on(self.sensodrive_initialization_message)

        elif (self._current_state_hex == 0x14):
            self.on_to_off(self.sensodrive_initialization_message)

        elif (self._current_state_hex == 0x18):
            self.clear_error(self.sensodrive_initialization_message)

    def off_to_on(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from off to on.
        :return:
        """
        print('off to on')
        message.DATA[0] = 0x10
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.001)

        message.DATA[0] = 0x12
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.001)

        message.DATA[0] = 0x14
        self.PCAN_object.Write(self._pcan_channel, message)

    def on_to_off(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from on to off.
        :return:
        """
        print('on to off')
        message.DATA[0] = 0x12
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.001)
        message.DATA[0] = 0x10
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.001)

    def clear_error(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from error to off.
        :return:
        """
        print('clear error')
        message.DATA[0] = 0x1F
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.001)
