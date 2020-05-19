from enum import Enum

from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.inputclasses.PCANBasic import *
from modules.hardwaremanager.action.settings import SensoDriveSettings
from modules.joanmodules import JOANModules

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox

import os

class SensoDriveSettingsDialog(QtWidgets.QDialog):
    def __init__(self, sensodrive_settings, parent=None):
        super().__init__(parent)
        self.sensodrive_settings = sensodrive_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/sensodrive_settings_ui.ui"), self)
        # if(self.sensodrive_settings.PCAN_object.GetStatus(PCAN_USBBUS1) != PCAN_ERROR_OK) and self.sensodrive_settings.pcan_initialization_result != PCAN_ERROR_OK:
        #     self.sensodrive_settings.pcan_initialization_result = self.sensodrive_settings.PCAN_object.Initialize(PCAN_USBBUS1,PCAN_BAUD_1M)
        if self.sensodrive_settings.pcan_initialization_result is None:
            self.sensodrive_settings.pcan_initialization_result = self.sensodrive_settings.PCAN_object.Initialize(PCAN_USBBUS1,PCAN_BAUD_1M)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self.show()

    def accept(self):
        print('jjoe')
        if self.sensodrive_settings.pcan_initialization_result != PCAN_ERROR_OK:
            answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                        (self.sensodrive_settings.PCAN_object.GetErrorText(self.sensodrive_settings.pcan_initialization_result)[1].decode("utf-8")\
                                                        + ". Do you want to continue?"),
                                                        buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Cancel:
                return
            if answer == QtWidgets.QMessageBox.Ok:
                self.sensodrive_settings.pcan_error = True
        else:
            self.sensodrive_settings.pcan_error = False

        super().accept()

        # Hier moeten alle settings van demping, veersterkte, frictie etc (zijn allemaal bytes in dezelfde message)

    def _set_default_values(self):
        print('Settings reset')
        #hier moeten de default settings

    

class JOAN_SensoDrive(BaseInput):  # DEPRECATED FOR NOW TODO: remove from interface for now
    def __init__(self, hardware_manager_action, sensodrive_tab, settings: SensoDriveSettings):
        super().__init__(hardware_manager_action)
        msg_box = QMessageBox()

        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self.settings = settings
        self.PCANError = False

        # Create PCAN object
        self.settings.PCAN_object = PCANBasic()
        self.settings.pcan_initialization_result = None

        


        #  hook up buttons
        self._sensodrive_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._sensodrive_tab.btn_visualization.setEnabled(False)
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)

        # Initialize message structures
        self.steering_wheel_message = TPCANMsg()
        self.pedal_message = TPCANMsg()

        # Initialize data structures
        self.steering_wheel_senddata = {}

        self._open_settings_dialog()

    def _open_settings_dialog(self):
        self.settings_dialog = SensoDriveSettingsDialog(self.settings)

        
    def remove_func(self):
        self.remove_tab(self._sensodrive_tab)

    def process(self):
        # # If there are cars in the simulation add them to the controllable car combobox
        if self._carla_interface_data['vehicles']:
            self._carla_interface_data = self._action.read_news(JOANModules.CARLA_INTERFACE)

            for vehicles in self._carla_interface_data['vehicles']:
                if vehicles.selected_input == self._sensodrive_tab.groupBox.title():
                    self._sensodrive_tab.btn_remove_hardware.setEnabled(False)
                    break
                else:
                    self._sensodrive_tab.btn_remove_hardware.setEnabled(True)

        

        # Throttle:
  
        self._data['ThrottleInput'] = 0

        # Brake:
        self._data['BrakeInput'] = 0
        
        # Steering:
        self._data['SteeringInput'] = 0

        # Reverse
        self._data['Reverse'] = 0

        # Handbrake
        self._data['Handbrake'] = 0

        return self._data

    def write_message_steering_wheel(self,pcan_object, pcanmessage, data):
        torque_bytes = int.to_bytes(data['torque'],2, byteorder = 'little',signed= True)
        friction_bytes = int.to_bytes(data['friction'],2, byteorder = 'little',signed= True)
        damping_bytes = int.to_bytes(data['damping'],2, byteorder = 'little',signed= True)
        spring_stiffness_bytes = int.to_bytes(data['spring_stiffness'],2, byteorder = 'little',signed= True)

        pcanmessage.ID = STEERINGWHEEL_MESSAGE_ID
        pcanmessage.LEN = STEERINGWHEEL_MESSAGE_LENGTH
        pcanmessage.DATA[0] = torque_bytes[0]
        pcanmessage.DATA[1] = torque_bytes[1]
        pcanmessage.DATA[2] = friction_bytes[0]
        pcanmessage.DATA[3] = friction_bytes[1]
        pcanmessage.DATA[4] = damping_bytes[0]
        pcanmessage.DATA[5] = damping_bytes[1]
        pcanmessage.DATA[6] = spring_stiffness_bytes[0]
        pcanmessage.DATA[7] = spring_stiffness_bytes[1]

        if not self.PCANError:
            self.PCAN_object.write(PCAN_USBBUS1, pcanmessage)





            


class MessageOut(Enum):
    INITIALIZATION_MESSAGE_ID = 0x200
    INITIALIZATION_MESSAGE_LENGTH = 8

    STEERINGWHEEL_MESSAGE_ID = 0x201
    STEERINGWHEEL_MESSAGE_LENGTH = 8

    PEDAL_MESSAGE_ID = 0x20C
    PEDAL_MESSAGE_LENGTH = 2
