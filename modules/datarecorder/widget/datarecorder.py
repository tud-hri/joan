from process import Control
import os
from PyQt5 import QtCore
from time import sleep
from modules.datarecorder.action.states import DatarecorderStates
from modules.datarecorder.action.datarecorder import DatarecorderAction

class DatarecorderWidget(Control):
    """ 
    DatarecorderWidget 
    """    
    
    ## Methods
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        kwargs['callback'] = [self.do]  # method will run each given millis

        Control.__init__(self, *args, **kwargs)
        self.createWidget(ui=os.path.join(os.path.dirname(os.path.realpath(__file__)),"datarecorder.ui"))
        self.data = {}
        self.writeNews(channel=self, news=self.data)

        self.millis = kwargs['millis']
        
        # creating a self.moduleStateHandler which also has the moduleStates in self.moduleStateHandler.states
        self.defineModuleStateHandler(module=self, moduleStates=DatarecorderStates())
        self.moduleStateHandler.stateChanged.connect(self.handlemodulestate)
        self.masterStateHandler.stateChanged.connect(self.handlemasterstate)

        try:
            self.action = DatarecorderAction(moduleStates = self.moduleStates,
                                             moduleStateHandler = self.moduleStateHandler)
        except Exception as inst:
            print('De error bij de constructor van de widget is:    ', inst)
       
    def do(self):
        #print(" counter %d" % self.counter)
        print("news from steeringcommunication", self.readNews('modules.steeringcommunication.widget.steeringcommunication.SteeringcommunicationWidget'))

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.widget.show()
        self.masterStateHandler.requestStateChange(self.moduleStates.IDLE)


        # ref, so we can find ourselves
        #self._haptictrainer = haptictrainer

        # connect buttons
        self.widget.btnInitialize.clicked.connect(self.action._clickedBtnInitialize)
        self.widget.btnStartRecorder.clicked.connect(self.action._clickedBtnStartRecorder)
        self.widget.btnStopRecorder.clicked.connect(self.action._clickedBtnStopRecorder)

        # disable the start and stop buttons
        self.widget.btnStartRecorder.setEnabled(False)
        self.widget.btnStopRecorder.setEnabled(False)
        
        '''
        # connect the signals from the data recorder; to be used to show messages or something
        self._haptictrainer.datarecorder.recordingStarted.connect(self._recordingStarted)
        self._haptictrainer.datarecorder.recordingFinished.connect(self._recordingFinished)

        self._haptictrainer.statehandler.stateChanged.connect(self._onStateChanged)
        '''

        # set current data file name
        self.widget.lblDataFilename.setText("< none >")

        # set message text
        self.widget.lblMessageRecorder.setText("not recording")
        self.widget.lblMessageRecorder.setStyleSheet('color: orange')

        self.widget.lblStatusRecorder.setText("not initialized")
        self.widget.lblStatusRecorder.setStyleSheet('color: orange')


    def start(self):
        if not self.widget.isVisible():
            self._show()
        self.startPulsar()

    def stop(self):
        self.stopPulsar()

    def _close(self):
        self.widget.close()

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        #self.masterStateHandler.stateChanged
        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.masterStateHandler.getState(state) # ensure we have the State object (not the int)
 
             # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self.stop()

            if stateAsState == self.moduleStates.INITIALIZED.DATARECORDER:
                self.widget.btnStartRecorder.setEnabled(True)
                self.widget.btnStopRecorder.setEnabled(True)
                #self.start()

            # update the state label
            self.widget.lblStatusRecorder.setText(stateAsState.name)

        except Exception as inst:
            print (inst)

    def handlemasterstate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        #self.masterStateHandler.stateChanged
        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.masterStateHandler.getState(state) # ensure we have the State object (not the int)
 
             # emergency stop
            if stateAsState == self.moduleStates.ERROR:
                self.stop()

            if stateAsState == self.moduleStates.INITIALIZED.DATARECORDER:
                self.widget.btnStartRecorder.setEnabled(True)
                self.widget.btnStopRecorder.setEnabled(True)
                #self.start()

            # update the state label
            self.widget.lblStatusRecorder.setText(stateAsState.name)

        except Exception as inst:
            print (inst)
