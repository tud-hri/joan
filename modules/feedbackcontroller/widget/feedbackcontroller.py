from process import Control, State, translate
from PyQt5 import QtCore, QtWidgets, uic
from modules.feedbackcontroller.action.states import FeedbackcontrollerStates
# from PyQt5.QtWidgets import QWidget
import os
from modules.feedbackcontroller.action.feedbackcontroller import *

class FeedbackcontrollerWidget(Control):
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"feedbackcontroller.ui"))
        
        self.data = {}
        self.writeNews(channel=self, news=self.data)
        self.counter = 0

        self.defineModuleStateHandler(module=self, moduleStates=FeedbackcontrollerStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)

        try:
            self.action = FeedbackcontrollerAction(moduleStates = self.moduleStates,
                                          moduleStateHandler = self.moduleStateHandler)
        except Exception as e:
            print('De error bij de constructor van de widget is: ', e)
        
        # Initiate the different classes (controllers) you want:
        self._controller = Basecontroller(self)
 
 
        #self.Controllers = {}
        self.Controllers = dict([("Manual",Manualcontrol(self)), ("FDCA", FDCAcontrol(self)), ("PD", PDcontrol(self))])

        #initialize controller with first one in the dict
        self._controller = self.Controllers["Manual"]


        self.widget.tabWidget.currentChanged.connect(self.changedControl)


    # callback class is called each time a pulse has come from the Pulsar class instance
    def do(self):
        SWangle = self._controller.process()

        self.data['SteeringWheelAngle'] = SWangle
        self.data['Throttle'] = 0.5
        self.writeNews(channel=self, news=self.data)





        
        
    
    def changedControl(self):
        self._controller = self.Controllers[self.widget.tabWidget.currentWidget().windowTitle()]

        print('control changed!')

        
    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.mainwidget.show()


    def start(self):
        if not self.mainwidget.isVisible():
            self._show()
        self.startPulsar()
        self.moduleStateHandler.requestStateChange(self.moduleStates.FEEDBACKCONTROLLER.RUNNING)
        

    def stop(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.FEEDBACKCONTROLLER.STOPPED)
        self.stopPulsar()

    def _close(self):
        self.mainwidget.close()


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
            self.widget.lblState.setText(str(stateAsState))

        except Exception as e:
            print (e)

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.moduleStateHandler.getState(state) # ensure we have the State object (not the int)
            
            # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self._stop()

            # update the state label
            self.mainwidget.lblModulestate.setText(str(stateAsState.name))

            if stateAsState == self.moduleStates.FEEDBACKCONTROLLER.RUNNING:
                self.mainwidget.btnStart.setStyleSheet("background-color: green")
            else:
                self.mainwidget.btnStart.setStyleSheet("background-color: none")

        except Exception as e:
            print(e)