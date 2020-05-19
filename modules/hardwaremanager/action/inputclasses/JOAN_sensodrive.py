from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.inputclasses.PCANBasic import *
from modules.hardwaremanager.action.settings import SensoDriveSettings
from modules.joanmodules import JOANModules

from PyQt5 import uic, QtWidgets

import os

class SensoDriveSettingsDialog(QtWidgets.QDialog):
    def __init__(self, sensodrive_settings, parent=None):
        super().__init__(parent)
        self.sensodrive_settings = sensodrive_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UIs/sensodrive_settings_ui.ui"), self)

        # self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(self._set_default_values)
        self.show()

    def accept(self):
        try:
            self.objPCAN = PCANBasic()
            # Initialize the PCAN object
            result = self.objPCAN.Initialize(PCAN_USBBUS1, PCAN_BAUD_1M)

            # Error handling if the result is not desired
            if result != PCAN_ERROR_OK:
                raise Exception (self.objPCAN.GetErrorText(result)[1])

            ## Construct the different messages to send to sensodrive (via CAN message)
            self.initMSG = TPCANMsg()
            self.controlMSG = TPCANMsg()

            self.initMSG.ID = 0x200
            self.initMSG.LEN = 8
            self.initMSG.MSGTYPE = PCAN_MESSAGE_STANDARD

            self.initMSG.DATA[0] = 10
            self.initMSG.DATA[1] =  0
            self.initMSG.DATA[2] =  0
            self.initMSG.DATA[3] =  0
            self.initMSG.DATA[4] = 0
            self.initMSG.DATA[5] =  0
            self.initMSG.DATA[6] = 0
            self.initMSG.DATA[7] =  0

            super().accept()


        except Exception as inst:
            print('Error', inst)

    

class JOAN_SensoDrive(BaseInput):  # DEPRECATED FOR NOW TODO: remove from interface for now
    def __init__(self, hardware_manager_action, sensodrive_tab, settings: SensoDriveSettings):
        super().__init__(hardware_manager_action)
        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self.settings = settings

        #  hook up buttons
        self._sensodrive_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._sensodrive_tab.btn_visualization.setEnabled(False)
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)

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
  

        # Steering:
        self._data['SteeringInput'] = 0

        # Reverse
        self._data['Reverse'] = 0

        # Handbrake
        self._data['Handbrake'] = 0

        return self._data
