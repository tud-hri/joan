from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput

from modules.hardwaremanager.action.settings import SensoDriveSettings
from modules.joanmodules import JOANModules

class JOAN_SensoDrive(BaseInput):  # DEPRECATED FOR NOW TODO: remove from interface for now
    def __init__(self, hardware_manager_action, sensodrive_tab, settings: SensoDriveSettings):
        super().__init__(hardware_manager_action)
        #raise NotImplementedError('Sensodrive input is not yet implemented')
        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)

    def remove_func(self):
        self.remove_tab(self._sensodrive_tab)



    # def initialize(self):
    #         print('Initializing...')
    #         try:
    #             # Make the PCAN object for CAN communication
    #             if platform.system in ('Windows', ):
    #                 self.objPCAN = PCANBasic()
    #                 # Initialize the PCAN object
    #                 result = self.objPCAN.Initialize(PCAN_USBBUS1, PCAN_BAUD_1M)

    #                 # Error handling if the result is not desired
    #                 if result != PCAN_ERROR_OK:
    #                     raise Exception (self.objPCAN.GetErrorText(result)[1])

    #                 ## Construct the different messages to send to sensodrive (via CAN message)
    #                 self.initMSG = TPCANMsg()
    #                 self.controlMSG = TPCANMsg()

    #                 self.initMSG.ID = 0x200
    #                 self.initMSG.LEN = 8
    #                 self.initMSG.MSGTYPE = PCAN_MESSAGE_STANDARD

    #                 self.initMSG.DATA[0] = 10
    #                 self.initMSG.DATA[1] =  0
    #                 self.initMSG.DATA[2] =  0
    #                 self.initMSG.DATA[3] =  0
    #                 self.initMSG.DATA[4] = 0
    #                 self.initMSG.DATA[5] =  0
    #                 self.initMSG.DATA[6] = 0
    #                 self.initMSG.DATA[7] =  0
                    

    #                 self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.INITIALIZED)
    #                 self.ready()
    #             else:
    #                 self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.ERROR.INIT)
    #                 self.stop()

    #         except Exception as inst:
    #             traceback.print_exc(file=sys.stdout)

    #             print(self.module_states)
    #             self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.ERROR.INIT)
                
    #             print('In initialize of action/steeringcommunication',inst)
    #             self.stop()
