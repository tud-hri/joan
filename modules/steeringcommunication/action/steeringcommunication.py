from process import Control
from modules.steeringcommunication.action.PCANBasic import *

class SteeringcommunicationAction(Control):
    def __init__(self, *args, **kwargs):
        kwargs['ui'] = None
        Control.__init__(self,*args, **kwargs)

        # Declare variables
        self.objPCAN = None
        self.initMSG = None
        self.controlMSG = None

    



            
    
    def initialize(self):
        print('Initializing...')
        try:
            # Make the PCAN object for CAN communication
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
            


            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.INITIALIZED)
            self.ready()
        except Exception as inst:
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.ERROR.INIT)
            
            print(inst)


    def ready(self):
        if(self.statehandler._state is self.states.STEERINGWHEEL.INITIALIZED):
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.READY)

    def start(self):
        print('Pressed Start')
        if(self.statehandler._state is self.states.STEERINGWHEEL.READY):
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.ON)

    def stop(self):
        print('Pressed Stop')
        if(self.statehandler._state is self.states.STEERINGWHEEL.ON):
            self.statehandler.requestStateChange(self.states.STEERINGWHEEL.READY)
