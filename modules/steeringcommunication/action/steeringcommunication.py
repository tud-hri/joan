from process import Control
from modules.steeringcommunication.action.PCANBasic import *
#from modules.steeringcommunication.action.states import SteeringcommunicationStates

import traceback
import sys
import platform

class SteeringcommunicationAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self,*args, **kwargs)
        self.moduleStates = None
        self.moduleStateHandler = None
        try:
            statePackage = self.getModuleStatePackages(module='module.steeringcommunication.widget.steeringcommunication.SteeringcommunicationWidget')
            self.moduleStates = statePackage['moduleStates']
            self.moduleStateHandler = statePackage['moduleStateHandler']
        except:
            pass
        # get state information from module Widget
        #self.moduleStates = 'moduleStates' in kwargs.keys() and kwargs['moduleStates'] or None
        #self.moduleStateHandler = 'moduleStateHandler' in kwargs.keys() and kwargs['moduleStateHandler'] or None

        #self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"steeringcommunication.ui"))
        #self.data = {}
        #self.data['throttle'] = 0
        #self.data['damping'] = 0
        #self.writeNews(channel=self, news=self.data)

        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        #self.defineModuleStateHandler(module=self, moduleStates=SteeringcommunicationStates())
        #self.moduleStateHandler.stateChanged.emit(self.moduleStateHandler.state)
        #self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        #self.masterStateHandler.stateChanged.connect(self.handlemasterstate)


        print('News', self.getAllNews())

        # Declare variables
        self.objPCAN = None
        self.initMSG = None
        self.controlMSG = None

    



            
    
    def initialize(self):
        print('Initializing...')
        try:
            # Make the PCAN object for CAN communication
            if platform.system in ('Windows', ):
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
                

                self.moduleStateHandler.requestStateChange(self.moduleStates.STEERINGWHEEL.INITIALIZED)
                self.ready()
            else:
                self.moduleStateHandler.requestStateChange(self.moduleStates.STEERINGWHEEL.ERROR.INIT)
                self.stop()

        except Exception as inst:
            traceback.print_exc(file=sys.stdout)

            print(self.moduleStates)
            self.moduleStateHandler.requestStateChange(self.moduleStates.STEERINGWHEEL.ERROR.INIT)
            
            print('In initialize of action/steeringcommunication',inst)
            self.stop()


    def ready(self):
        if(self.moduleStateHandler._state is self.moduleStates.STEERINGWHEEL.INITIALIZED):
            self.moduleStateHandler.requestStateChange(self.moduleStates.STEERINGWHEEL.READY)

    def start(self):
        print('Pressed Start')
        if(self.moduleStateHandler._state is self.moduleStates.STEERINGWHEEL.READY):
            self.moduleStateHandler.requestStateChange(self.moduleStates.STEERINGWHEEL.ON)

    def stop(self):
        print('Pressed Stop')
        if(self.moduleStateHandler._state is self.moduleStates.STEERINGWHEEL.ON):
            self.moduleStateHandler.requestStateChange(self.moduleStates.STEERINGWHEEL.READY)

