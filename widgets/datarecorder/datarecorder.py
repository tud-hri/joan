from process import Control
import os
from PyQt5 import QtCore
from time import sleep

class DataRecorderWidget(Control):
    """ 
    DataRecorderWidget 
    """    
    
    ## Methods
    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 200
        kwargs['callback'] = [self.do]  # method will run each given millis

        kwargs['ui'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),"datarecorder.ui")
        Control.__init__(self, *args, **kwargs)

        self.counter = 0
        
        self.statehandler.stateChanged.connect(self.handlestate)
        self.statehandler.stateChanged.emit(self.statehandler.state)
        #self.statehandler.requestStateChange(self.states.IDLE)


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

    def do(self):
        self.counter += 1
        #print(" counter %d" % self.counter)
        if (self.counter == 100):
            self.statehandler.stateChanged.emit(self.statehandler.state)

            self.statehandler.requestStateChange(self.states.INITIALIZED)
        self.widget.btnInitialize.setText(str(self.counter))

    def handlestate(self, state):
        """ 
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """

        print("gedaan in datarecorder", state, self.gui)
        #self.statehandler.stateChanged
        try:
            stateAsState = self.states.getState(state) # ensure we have the State object (not the int)
            # update the state label
            self.widget.lblDataFilename.setText(str(stateAsState))
        except Exception as inst:
            print (inst)


    def show(self):
        self.startPulsar()
        self.widget.show()


    def _clickedBtnInitialize(self):
        """initialize the data recorder (mainly setting the data directory and data file prefix"""
        self._haptictrainer.datarecorder.initialize()

    def _clickedBtnStartRecorder(self):
        """ btnStartRecorder clicked. """
        if self._haptictrainer.datarecorder.initialized:
            # request state change to DEBUG.DATARECORDER
            self._haptictrainer.statehandler.requestStateChange(self.states.DEBUG.DATARECORDER.START)

        # To-do: check whether State change has been made and state is actually running without errors If not,
        # go back to previous state

    def _clickedBtnStopRecorder(self):
        """ btnStopRecorder clicked. """
        self._haptictrainer.statehandler.requestStateChange(self.states.INITIALIZED.INTERFACE)

        # set current data file name
        # self.lblDataFilename.setText('< none >')

    def _onStateChanged(self, state):
        """ state changed """
        if self._haptictrainer.datarecorder.initialized:
            self.btnStartRecorder.setEnabled(True)
            self.btnStopRecorder.setEnabled(True)
            self.lblStatusRecorder.setText("initialized")
            self.lblStatusRecorder.setStyleSheet('color: green')
        else:
            self.lblStatusRecorder.setText("not initialized")
            self.lblStatusRecorder.setStyleSheet('color: orange')

    def _recordingStarted(self):
        """
        Recording started, change messages and current data file label.
        This function is called when a _recordingStarted signal has been emitted (by the datarecorder class)
        """

        # set current data file name
        self.lblDataFilename.setText(self._haptictrainer.datarecorder.currentFilename)

        # show message
        self.lblMessageRecorder.setText("recording")
        self.lblMessageRecorder.setStyleSheet('color: green')
        
    def _recordingFinished(self):
        """ recording has finished, change messages """

        # set current data file name
        self.lblDataFilename.setText("< none >")

        # show message
        self.lblMessageRecorder.setText("not recording")
        self.lblMessageRecorder.setStyleSheet('color: orange')