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
        #if self.moduleStateHandler.getCurrentState() == self.moduleStates.DATARECORDER.START:
        print("news from steeringcommunication", self.readNews('modules.steeringcommunication.widget.steeringcommunication.SteeringcommunicationWidget'))
        self.action.write(self.readNews('modules.steeringcommunication.widget.steeringcommunication.SteeringcommunicationWidget'))

    @QtCore.pyqtSlot(str)
    def _setmillis(self, millis):
        try:
            millis = int(millis)
            self.setInterval(millis)
        except:
            pass

    def _show(self):
        self.widget.show()
        self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.NOTINITIALIZED)

       # ref, so we can find ourselves
        #self._haptictrainer = haptictrainer

        # connect buttons
        self.widget.btnInitialize.clicked.connect(self._clickedBtnInitialize)
        self.widget.btnStartRecorder.clicked.connect(self._clickedBtnStartRecorder)
        self.widget.btnStopRecorder.clicked.connect(self._clickedBtnStopRecorder)

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
        self.action.stop()

    def _close(self):
        self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.STOP)
        self.widget.close()

    def handlemodulestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        #self.masterStateHandler.stateChanged
        try:
            #stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            stateAsState = self.moduleStateHandler.getState(state) # ensure we have the State object (not the int)

            if stateAsState == self.moduleStates.INITIALIZED.DATARECORDER:
                self.widget.btnStartRecorder.setEnabled(True)
                self.widget.lblStatusRecorder.setStyleSheet('color: green')
                self.action.initialize()

            if stateAsState == self.moduleStates.DATARECORDER.NOTINITIALIZED:
                self.widget.btnStartRecorder.setEnabled(False)
                self.widget.btnStopRecorder.setEnabled(False)
                self.widget.lblStatusRecorder.setStyleSheet('color: orange')

            if stateAsState == self.moduleStates.DATARECORDER.START:
                self.widget.btnStartRecorder.setEnabled(False)
                self.widget.btnInitialize.setEnabled(False)
                self.widget.btnStopRecorder.setEnabled(True)
                # set message text
                self.widget.lblMessageRecorder.setText("Busy Recording ...")
                self.widget.lblMessageRecorder.setStyleSheet('color: green')

                self.start()  # Pulsar

            if stateAsState == self.moduleStates.DATARECORDER.STOP:
                self.stop()   # Pulsar
                self.widget.btnStartRecorder.setEnabled(False)
                self.widget.btnStopRecorder.setEnabled(False)
                self.widget.btnInitialize.setEnabled(True)
                self.widget.lblStatusRecorder.setStyleSheet('color: orange')
                # set message text
                self.widget.lblMessageRecorder.setText("not recording")
                self.widget.lblMessageRecorder.setStyleSheet('color: orange')

            # update the state label
            self.widget.lblStatusRecorder.setText(stateAsState.name)
            self.widget.repaint()

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
            if stateAsState == self.masterStates.ERROR:
                self.stop()
                self.widget.btnStartRecorder.setEnabled(False)
                self.widget.btnStopRecorder.setEnabled(False)
                self.widget.btnInitialize.setEnabled(True)
                self.widget.lblStatusRecorder.setStyleSheet('color: orange')

            # update the state label
            self.widget.lblStatusRecorder.setText(stateAsState.name)
            self.widget.repaint()

        except Exception as inst:
            print (inst)

    def _clickedBtnInitialize(self):
        """initialize the data recorder (mainly setting the data directory and data file prefix"""
        self.moduleStateHandler.requestStateChange(self.moduleStates.INITIALIZED.DATARECORDER)
        pass
        #if self.action.initialize():
        # set current data file name
        # self.lblDataFilename.setText('< none >')        #self._haptictrainer.datarecorder.initialize()

    def _clickedBtnStartRecorder(self):
        """ btnStartRecorder clicked. """
        if self.moduleStateHandler.getCurrentState() != self.moduleStates.DATARECORDER.START:
            #if self._haptictrainer.datarecorder.initialized:
                # request state change to DEBUG.DATARECORDER
            self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.START)
            #if self.action.startRecording():

            # To-do: check whether State change has been made and state is actually running without errors If not,
            # go back to previous state

    def _clickedBtnStopRecorder(self):
        """ btnStopRecorder clicked. """
        if self.moduleStateHandler.getCurrentState() != self.moduleStates.DATARECORDER.STOP:
            self.moduleStateHandler.requestStateChange(self.moduleStates.DATARECORDER.STOP)
            #self.action.stopRecording()


