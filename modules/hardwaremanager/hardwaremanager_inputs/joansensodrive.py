import math
import multiprocessing as mp
import os
import queue
import time

from PyQt5 import uic, QtWidgets

from modules.hardwaremanager.hardwaremanager_inputs.PCANBasic import *
from modules.hardwaremanager.hardwaremanager_inputtypes import HardwareInputTypes

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


class JOANSensoDriveProcess:
    def __init__(self, settings, shared_variables):
        super().__init__()

        # We define our settings list which contains only picklable objects
        self.settings_dict = settings.settings_dict_for_pipe()

        # We will write all the output of the sensodrive to these variables so that we have it in our main joan program
        self.shared_variables = shared_variables

        # Initialize communication pipe between seperate sensodrive process
        self.parent_pipe, child_pipe = mp.Pipe(duplex=True)


        # Create the sensodrive communication object with needed events and pipe
        comm = SensoDriveComm(turn_on_event=settings.events.turn_on_event, turn_off_event=settings.events.turn_off_event,
                              close_event=settings.events.close_event, clear_error_event=settings.events.clear_error_event,
                              child_pipe=child_pipe, state_queue=settings.events.state_queue)

        # Start the communication process when it is created

        self.shared_variables.torque = settings.torque
        self.shared_variables.friction = settings.friction
        self.shared_variables.damping = settings.damping
        self.shared_variables.auto_center_stiffness = settings.spring_stiffness

        comm.start()
        self.parent_pipe.send(self.settings_dict)

    def update_variables(self):
        # 'variable settings' (can be changed at runtime through the shared variables)
        self.settings_dict['friction'] = self.shared_variables.friction
        self.settings_dict['damping'] = self.shared_variables.damping
        self.settings_dict['spring_stiffness'] = self.shared_variables.loha_stiffness + self.shared_variables.auto_center_stiffness

    def do(self):
        # 'variable settings' (can be changed at runtime through the shared variables)
        print(self.shared_variables.auto_center_stiffness, self.shared_variables.loha_stiffness)
        self.settings_dict['torque'] = self.shared_variables.torque
        self.settings_dict['friction'] = self.shared_variables.friction
        self.settings_dict['damping'] = self.shared_variables.damping
        self.settings_dict['spring_stiffness'] = self.shared_variables.loha_stiffness + self.shared_variables.auto_center_stiffness

        self.parent_pipe.send(self.settings_dict)
        values_from_sensodrive = self.parent_pipe.recv()
        self.shared_variables.steering_angle = values_from_sensodrive['steering_angle']
        self.shared_variables.throttle = values_from_sensodrive['throttle']
        self.shared_variables.brake = values_from_sensodrive['brake']
        self.shared_variables.steering_rate = values_from_sensodrive['steering_rate']

class SensoDriveSettings:
    """
    Default sensodrive settings that will load whenever a keyboardinput class is created.
    """

    def __init__(self, identifier=''):
        self.endstops = math.radians(360.0)  # rad
        self.torque_limit_between_endstops = 200  # percent
        self.torque_limit_beyond_endstops = 200  # percent
        self.friction = 0  # Nm
        self.damping = 0.1  # Nm * s / rad
        self.spring_stiffness = 1  # Nm / rad
        self.torque = 0  # Nm
        self.identifier = identifier
        self.input_type = HardwareInputTypes.SENSODRIVE.value

        self.current_state = 0x00

        self.settings_dict = {}

    def as_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.identifier)

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

    def settings_dict_for_pipe(self):
        self.settings_dict = {'endstops': self.endstops,  # rad
                              'torque_limit_between_endstops': self.torque_limit_between_endstops,  # percent
                              'torque_limit_beyond_endstops': self.torque_limit_beyond_endstops,  # percent
                              'friction': self.friction,  # Nm
                              'damping': self.damping,  # Nm * s / rad
                              'spring_stiffness': self.spring_stiffness,  # Nm / rad
                              'torque': self.torque,  # Nm
                              'identifier': self.identifier}

        return self.settings_dict


class SensoDriveSettingsDialog(QtWidgets.QDialog):
    """
    Class for the settings Dialog of a SensoDrive, this class should pop up whenever it is asked by the user or when
    creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
    """

    def __init__(self, module_manager, settings=None, parent=None):
        super().__init__(parent)
        self.sensodrive_settings = settings
        self.module_manager = module_manager
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/sensodrive_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)

        self.btn_apply.clicked.connect(self.update_parameters)

        self._display_values()
        self.show()

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
        
        # try:
        #     # TODO, dit moet op de een of andere manier nog in de ready state ook gaan werken (werkt nu alleen in running)
        #     self.module_manager.shared_variables.inputs[self.sensodrive_settings.identifier].friction = self.sensodrive_settings.friction
        #     self.module_manager.shared_variables.inputs[self.sensodrive_settings.identifier].damping = self.sensodrive_settings.damping
        #     self.module_manager.shared_variables.inputs[self.sensodrive_settings.identifier].spring_stiffness = self.sensodrive_settings.spring_stiffness
        # except Exception as inst:
        #     print(inst)

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

        # try:
        #     self.module_manager._process.input_objects[self.sensodrive_settings.identifier].update_variables()
        #     self.module_manager.shared_variables.inputs[self.sensodrive_settings.identifier].friction = self.sensodrive_settings.friction
        #     self.module_manager.shared_variables.inputs[self.sensodrive_settings.identifier].damping = self.sensodrive_settings.damping
        #     self.module_manager.shared_variables.inputs[self.sensodrive_settings.identifier].spring_stiffness = self.sensodrive_settings.spring_stiffness
        # except:
        #     print('werkt niet')

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


def clear_queue(q):
    try:
        while True:
            q.get_nowait()
    except queue.Empty:
        pass


class SensoDriveComm(mp.Process):
    """
    This class is a seperate mp.Process which will start when it is created. It loops at approximately 10ms to keep the sensodrive from shutting off due to
    the watchdog.
    """

    def __init__(self, turn_on_event, turn_off_event, close_event, clear_error_event, child_pipe, state_queue):
        """
        Initialize the class with events and communication parameters: child_pipe and state_queue

        :param turn_on_event: signals sensodrive to turn on
        :param turn_off_event: signals sensodrive to turn off
        :param close_event:  closes down the communication and breaks out of loop
        :param clear_error_event: clears error state of sensodrive
        :param child_pipe: pipe to send values back to mp process
        :param state_queue: queue to send state to the rest of JOAN
        """
        super().__init__(daemon=True)
        self.turn_on_event = turn_on_event
        self.child_pipe = child_pipe
        self.turn_off_event = turn_off_event
        self.state_queue = state_queue
        self.clear_error_event = clear_error_event
        self.close_event = close_event
        self.values_from_sensodrive = {}

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

    def run(self):
        self.settings_dict = self.child_pipe.recv()
        if self.settings_dict['identifier'] == 'SensoDrive_1':
            self._pcan_channel = PCAN_USBBUS1
        else:
            self._pcan_channel = PCAN_USBBUS2
        self._time_step_in_ns = 10000000
        # Here we can initialize our PCAN Communication (WE HAVE TO DO THIS HERE ELSE WE WONT HAVE THE PCAN OBJECT IN OUR DESIRED PROCESS
        self.initialize()

        while True:
            t0 = time.perf_counter_ns()
            self._time = time.perf_counter_ns()

            data_available = self.child_pipe.poll()
            if data_available is True:
                self.settings_dict = self.child_pipe.recv()
                self.child_pipe.send(self.values_from_sensodrive)

            # convert SI units to Sensowheel units
            self.steering_wheel_parameters = self._map_si_to_sensodrive(self.settings_dict)

            # send steering wheel data
            self.write_message_steering_wheel(self.pcan_object, self.steering_wheel_message, self.steering_wheel_parameters)

            # receive data from Sensodrive (wheel, pedals)
            received = self.pcan_object.Read(self._pcan_channel)

            # request state data
            endstops_bytes = int.to_bytes(int(math.degrees(self.settings_dict['endstops'])), 2, byteorder='little', signed=True)
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

            if self.turn_off_event.is_set():
                self.on_to_off(self.state_message)
                self.turn_off_event.clear()

            if self.turn_on_event.is_set():
                self.off_to_on(self.state_message)
                self.turn_on_event.clear()

            if self.clear_error_event.is_set():
                self.clear_error(self.state_message)
                self.clear_error_event.clear()

            # TODO: Have to fix this stuff when we have the variable settings
            # if self.update_settings_event.is_set():
            # self.update_settings()
                # self.update_settings_event.clear()

            # properly uninitialize the pcan dongle if sensodrive is removed
            if self.close_event.is_set():
                self.close_event.clear()
                # send last known values over the pipe
                self.child_pipe.send(self.values_from_sensodrive)
                self.child_pipe.close()
                clear_queue(self.state_queue)
                self.state_queue.put(self._current_state_hex)
                self.pcan_object.Uninitialize(self._pcan_channel)
                break

            clear_queue(self.state_queue)
            self.state_queue.put(self._current_state_hex)
            pass

            execution_time = time.perf_counter_ns() - t0

            # sleep for time step, taking the execution time into account
            time.sleep(max(0.0, (self._time_step_in_ns - execution_time) * 1e-9))

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
        message.DATA[0] = 0x10
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.00001)

        message.DATA[0] = 0x12
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.00001)

        message.DATA[0] = 0x14
        self.pcan_object.Write(self._pcan_channel, message)

    def on_to_off(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from on to off.
        :return:
        """
        message.DATA[0] = 0x12
        self.pcan_object.Write(self._pcan_channel, message)
        time.sleep(0.00001)
        message.DATA[0] = 0x10
        self.pcan_object.Write(self._pcan_channel, message)

    def clear_error(self, message):
        """
        If a PCAN dongle is connected and working will try to move the state of the sensodrive from error to off.
        :return:
        """
        message.DATA[0] = 0x1F
        self.pcan_object.Write(self._pcan_channel, message)

    def initialize(self):
        self.pcan_object = PCANBasic()
        self.pcan_initialization_result = self.pcan_object.Initialize(self._pcan_channel, PCAN_BAUD_1M)

        # Convert our shared settings to bytes
        endstops_bytes = int.to_bytes(int(math.degrees(self.settings_dict['endstops'])), 2, byteorder='little', signed=True)
        torque_limit_between_endstops_bytes = int.to_bytes(self.settings_dict['torque_limit_between_endstops'], 1, byteorder='little',
                                                           signed=False)
        torque_limit_beyond_endstops_bytes = int.to_bytes(self.settings_dict['torque_limit_beyond_endstops'], 1, byteorder='little',
                                                          signed=False)

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
        # time.sleep(0.002)
        self.pcan_object.Read(self._pcan_channel)

        # do not switch mode
        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

        # Set the data structure for the steeringwheel message with the just applied values
        self.steering_wheel_parameters = self._map_si_to_sensodrive(self.settings_dict)

        self.pcan_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        # time.sleep(0.02)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]

        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

    def _map_si_to_sensodrive(self, settings):
        # convert SI units to Sensowheel units

        out = {
            'torque': int(settings['torque'] * 1000.0),
            'friction': int(settings['friction'] * 1000.0),
            'damping': int(settings['damping'] * 1000.0 * (2.0 * math.pi) / 60.0),
            'spring_stiffness': int(settings['spring_stiffness'] * 1000.0 / (180.0 / math.pi))
        }

        return out

    def _sensodrive_data_to_si(self, received):
        if received[1].ID == STEERINGWHEEL_MESSAGE_RECEIVE_ID:
            # steering wheel

            # steering angle
            increments = int.from_bytes(received[1].DATA[0:4], byteorder='little', signed=True)
            self.values_from_sensodrive['steering_angle'] = math.radians(float(increments) * 0.009)  # we get increments, convert to deg, convert to rad

            # steering rate
            steering_rate = int.from_bytes(received[1].DATA[4:6], byteorder='little', signed=True)
            self.values_from_sensodrive['steering_rate'] = float(steering_rate) * (2.0 * math.pi) / 60.0  # we get rev/min, convert to rad/s

            # torque
            torque = int.from_bytes(received[1].DATA[6:], byteorder='little', signed=True)
            self.values_from_sensodrive['measured_torque'] = float(torque) / 1000.0  # we get mNm convert to Nm

        elif received[1].ID == PEDAL_MESSAGE_RECEIVE_ID:
            # pedals
            self.values_from_sensodrive['throttle'] = float(int.from_bytes(received[1].DATA[2:4], byteorder='little') - 1100) / 2460.0
            self.values_from_sensodrive['brake'] = float(int.from_bytes(received[1].DATA[4:6], byteorder='little') - 1) / 500

        elif received[1].ID == STATE_MESSAGE_RECEIVE_ID:
            #
            self._current_state_hex = received[1].DATA[0]
            self.values_from_sensodrive['sensodrive_motorstate'] = received[1].DATA[0]

    def update_settings(self):
        endstops_bytes = int.to_bytes(int(math.degrees(self.settings_dict['endstops'])), 2, byteorder='little', signed=True)
        torque_limit_between_endstops_bytes = int.to_bytes(self.settings_dict['torque_limit_between_endstops'], 1, byteorder='little',
                                                           signed=False)
        torque_limit_beyond_endstops_bytes = int.to_bytes(self.settings_dict['torque_limit_beyond_endstops'], 1, byteorder='little',
                                                          signed=False)

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
        # time.sleep(0.002)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]


