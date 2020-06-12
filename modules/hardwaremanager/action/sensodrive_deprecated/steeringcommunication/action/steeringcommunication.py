from modules.steeringcommunication.action.PCANBasic import *
#from modules.steeringcommunication.action.states import SteeringcommunicationStates

import traceback
import sys
import platform

class SteeringcommunicationAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.module_states = None
        self.module_state_handler = None
        try:
            state_package = self.get_module_state_package(module='modules.steeringcommunication.widget.steeringcommunication.SteeringcommunicationWidget')
            self.module_states = state_package['module_states']
            self.module_state_handler = state_package['module_state_handler']
        except:
            pass
        # get state information from module Widget
        #self.module_states = 'module_states' in kwargs.keys() and kwargs['module_states'] or None
        #self.module_state_handler = 'module_state_handler' in kwargs.keys() and kwargs['module_state_handler'] or None

        #self.create_widget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"steeringcommunication.ui"))
        #self.data = {}
        #self.data['throttle'] = 0
        #self.data['damping'] = 0
        #self.write_news(channel=self, news=self.data)

        # creating a self.module_state_handler which also has the module_states in self.module_state_handler.states
        #self.define_module_state_handler(module=self, module_states=SteeringcommunicationStates())
        #self.module_state_handler.state_changed.emit(self.module_state_handler.state)
        #self.module_state_handler.state_changed.connect(self.handle_module_state)
        #self.master_state_handler.state_changed.connect(self.handle_master_state)


        #print('News in action/steeringcommunication.py', self.get_all_news())

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
                

                self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.INITIALIZED)
                self.ready()
            else:
                self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.ERROR.INIT)
                self.stop()

        except Exception as inst:
            traceback.print_exc(file=sys.stdout)

            print(self.module_states)
            self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.ERROR.INIT)
            
            print('In initialize of action/steeringcommunication',inst)
            self.stop()


    def ready(self):
        if(self.module_state_handler._state is self.module_states.STEERINGWHEEL.INITIALIZED):
            self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.READY)

    def start(self):
        print('Pressed Start')
        if(self.module_state_handler._state is self.module_states.STEERINGWHEEL.READY):
            self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.ON)

    def stop(self):
        print('Pressed Stop')
        if(self.module_state_handler._state is self.module_states.STEERINGWHEEL.ON):
            self.module_state_handler.request_state_change(self.module_states.STEERINGWHEEL.READY)

