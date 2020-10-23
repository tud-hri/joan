import math
import multiprocessing as mp
import time

from modules.hardwaremanager.action.inputclasses.PCANBasic import *

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
        self.sensodrive_shared_variables = shared_variables

        # if connecting more Sensowheels, different USB/PCAN bus
        if self.sensodrive_shared_variables.sensodrive_ID == 0:
            self._pcan_channel = PCAN_USBBUS1
        elif self.sensodrive_shared_variables.sensodrive_ID == 1:
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
        endstops_bytes = int.to_bytes(int(math.degrees(self.sensodrive_shared_variables.endstops)), 2, byteorder='little', signed=True)
        torque_limit_between_endstops_bytes = int.to_bytes(self.sensodrive_shared_variables.torque_limit_between_endstops, 1, byteorder='little', signed=False)
        torque_limit_beyond_endstops_bytes = int.to_bytes(self.sensodrive_shared_variables.torque_limit_beyond_endstops, 1, byteorder='little', signed=False)

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

        # do not switch mode
        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

        # Set the data structure for the steeringwheel message with the just applied values
        self.steering_wheel_parameters = self._map_si_to_sensodrive(self.sensodrive_shared_variables)

        # TODO Do we need to do this twice?
        self.pcan_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.02)
        response = self.pcan_object.Read(self._pcan_channel)

        self._current_state_hex = response[1].DATA[0]

        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11
        print(hex(self._current_state_hex))
        self.sensodrive_shared_variables.sensodrive_motorstate = self._current_state_hex

        # self._current_state_hex = 0x00

    def update_settings(self):
        endstops_bytes = int.to_bytes(int(math.degrees(self.sensodrive_shared_variables.endstops)), 2, byteorder='little', signed=True)
        torque_limit_between_endstops_bytes = int.to_bytes(self.sensodrive_shared_variables.torque_limit_between_endstops, 1, byteorder='little', signed=False)
        torque_limit_beyond_endstops_bytes = int.to_bytes(self.sensodrive_shared_variables.torque_limit_beyond_endstops, 1, byteorder='little', signed=False)

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
        self.sensodrive_shared_variables.sensodrive_motorstate = self._current_state_hex
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
            self.sensodrive_shared_variables.steering_angle = math.radians(float(increments) * 0.009)  # we get increments, convert to deg, convert to rad

            # steering rate
            steering_rate = int.from_bytes(received[1].DATA[4:6], byteorder='little', signed=True)
            self.sensodrive_shared_variables.steering_rate = float(steering_rate) * (2.0 * math.pi) / 60.0  # we get rev/min, convert to rad/s

            # torque
            torque = int.from_bytes(received[1].DATA[6:], byteorder='little', signed=True)
            self.sensodrive_shared_variables.measured_torque = float(torque) / 1000.0  # we get mNm convert to Nm

        elif received[1].ID == PEDAL_MESSAGE_RECEIVE_ID:
            # pedals
            self.sensodrive_shared_variables.throttle = float(int.from_bytes(received[1].DATA[2:4], byteorder='little') - 1100) / 2460.0
            self.sensodrive_shared_variables.brake = float(int.from_bytes(received[1].DATA[4:6], byteorder='little') - 1) / 500

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
            self.steering_wheel_parameters = self._map_si_to_sensodrive(self.sensodrive_shared_variables)

            # send steering wheel data
            self.write_message_steering_wheel(self.pcan_object, self.steering_wheel_message, self.steering_wheel_parameters)

            # receive data from Sensodrive (wheel, pedals)
            received = self.pcan_object.Read(self._pcan_channel)

            # request state data
            endstops_bytes = int.to_bytes(int(math.degrees(self.sensodrive_shared_values.endstops)), 2, byteorder='little', signed=True)
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

            self.sensodrive_shared_values.sensodrive_motorstate = self._current_state_hex

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

    # def on_off(self):
    #     """
    #     If a PCAN dongle is connected and working will check what state the sensodrive is in and take the appropriate action
    #     (0x10 is ready, 0x14 is on and 0x18 is error)
    #     :return:
    #     """
    #     if self._current_state_hex == 0x10:
    #         self.off_to_on(self.sensodrive_initialization_message)
    #
    #     elif self._current_state_hex == 0x14:
    #         self.on_to_off(self.sensodrive_initialization_message)
    #
    #     elif self._current_state_hex == 0x18:
    #         self.clear_error(self.sensodrive_initialization_message)

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
        self.sensodrive_shared_values.sensodrive_motorstate = self._current_state_hex




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
        self.sensodrive_shared_values.sensodrive_motorstate = self._current_state_hex

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
        self.sensodrive_shared_values.sensodrive_motorstate = self._current_state_hex
