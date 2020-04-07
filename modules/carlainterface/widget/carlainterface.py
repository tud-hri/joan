from process import Control, State, translate
from PyQt5 import QtCore
import os
from modules.carlainterface.action.states import CarlainterfaceStates
from modules.carlainterface.action.carlainterface import Carlacommunication
from modules.carlainterface.action.carlainterface import Carlavehicle

class CarlainterfaceWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 100
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"carlainterfaceWidget.ui"))

        self.data = {}
        self.writeNews(channel=self, news=self.data)
        self.counter = 0

        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        self.defineModuleStateHandler(module=self, moduleStates=CarlainterfaceStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)

        try:
            self.action = Carlacommunication(self)
        except Exception as inst:
            print('De error bij de constructor van de carlainterface widget is:    ', inst)

        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION)
        self.widget.spinVehicles.setRange(0,10)
        self.widget.spinVehicles.lineEdit().setReadOnly(True)
        self.widget.spinVehicles.valueChanged.connect(self.updateCars)
        self.vehicles = []
 

    def updateCars(self):
        # Delete excess vehicles if any
        if(self.widget.spinVehicles.value() < len(self.vehicles)):
            for k in range(self.widget.spinVehicles.value(), len(self.vehicles)):
                self.vehicles[-k].destroy()
                self.vehicles.pop(-k)

        # Create new vehicles and show them:
        for i in range(len(self.vehicles), self.widget.spinVehicles.value()):
            self.vehicles.append(Carlavehicle(self, i))

        print(len(self.vehicles))

        



    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        self.data = self.action.getData() #get data from carla
        self.writeNews(channel=self, news=self.data)  #write away this data to news channel

        FeedbackControllerData = self.readNews('modules.feedbackcontroller.widget.feedbackcontroller.FeedbackcontrollerWidget')
        InputData = self.readNews('modules.hardwarecommunication.widget.hardwarecommunication.HardwarecommunicationWidget')
        print(InputData)

        try:
            self.action.setInputs(InputData)
        except:
            pass
        #print(InputData)
        #self.action.handleFeedbackcontrollerdata(FeedbackControllerData)


    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        try:
            self.window.show()
        except Exception as e:
            print(' ############## Exception was: #########',e)

    def start(self):
        if not self.window.isVisible():
            self._show()

        # Connect to the server
        Connected = self.action.start()
        self.data = self.action.getData()
        self.writeNews(channel=self, news=self.data)
        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION.RUNNING)
        self.startPulsar()

        #if Connected is True:
        #    self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION.RUNNING)
        #    self.startPulsar()
        #    print('STARTED CARLA PULSAR!!')

    def stop(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION.STOPPED)
        self.action.stop()
        
        self.stopPulsar()

    def _close(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.SIMULATION.STOPPED)
        # self.action.stop()
        # self.stopPulsar()
        # del self.action
        self.window.close()

    def handlemasterstate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.masterStateHandler.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.stateWidget.lblState.setText(str(stateAsState))

        except Exception as inst:
            print (inst)

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.moduleStateHandler.getState(state) # ensure we have the State object (not the int)]
            self.writeNews(channel=self, news=self.data)
            
            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.stateWidget.lblModuleState.setText(str(stateAsState.name))

            if stateAsState == self.moduleStates.SIMULATION.RUNNING:
                self.stateWidget.btnStart.setStyleSheet("background-color: green")
            else:
                self.stateWidget.btnStart.setStyleSheet("background-color: none")
            

        except Exception as inst:
            print (inst)
