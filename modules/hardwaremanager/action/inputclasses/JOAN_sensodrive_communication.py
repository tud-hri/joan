import multiprocessing as mp
from modules.hardwaremanager.action.inputclasses.PCANBasic import *
import time

"""
These global parameters are used to make the message ID's more identifiable than just the hex nr.
"""
INITIALIZATION_MESSAGE_ID = 0x200
INITIALIZATION_MESSAGE_LENGTH = 8

STEERINGWHEEL_MESSAGE_ID = 0x201
STEERINGWHEEL_MESSAGE_LENGTH = 8

PEDAL_MESSAGE_ID = 0x20C
PEDAL_MESSAGE_LENGTH = 2


class SensoDriveComm(mp.Process):
    def __init__(self, shared_values, init_event, toggle_event, close_event, update_event, shutoff_event):
        super().__init__()
        self.init_event = init_event
        self.toggle_sensodrive_motor_event = toggle_event
        self.close_event = close_event
        self.update_settings_event = update_event
        self.shutoff_event = shutoff_event

        # Create PCAN object
        self.pcan_initialization_result = None
        self.sensodrive_shared_values = shared_values
        print(self.sensodrive_shared_values.sensodrive_ID)
        if self.sensodrive_shared_values.sensodrive_ID == 0:
            self._pcan_channel = PCAN_USBBUS1
        elif self.sensodrive_shared_values.sensodrive_ID == 1:
            self._pcan_channel = PCAN_USBBUS2

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
            #Turn off sensodrive immediately (only when torque limits are breached)
            if self.shutoff_event.is_set():
                self.on_to_off(self.state_message)
                self.shutoff_event.clear()
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