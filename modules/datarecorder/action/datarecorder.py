from process import Control
#from queue import Queue

class DatarecorderAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.moduleStates = None
        self.moduleStateHandler = None
        try:
            statePackage = self.getModuleStatePackages(module='module.datarecorder.widget.daterecorder.DatarecorderWidget')
            self.moduleStates = statePackage['moduleStates']
            self.moduleStateHandler = statePackage['moduleStateHandler']
        except:
            pass

    def initialize(self):
        print('Initialize in action/datarecorder')
        # search for filename
        # create threaded filehandler(s)

    def write(self, news):
        #print('write the news data')
        print('in action/datarecorder', news)
        

    def stop(self):
        print('close the threaded filehandle(s)')
    '''
    def _clickedBtnInitialize(self):
        """initialize the data recorder (mainly setting the data directory and data file prefix"""
        self.moduleStateHandler.requestStateChange(self.moduleStates.INITIALIZED.DATARECORDER)
        pass
        #self._haptictrainer.datarecorder.initialize()

    def _clickedBtnStartRecorder(self):
        """ btnStartRecorder clicked. """
        #if self._haptictrainer.datarecorder.initialized:
            # request state change to DEBUG.DATARECORDER
        self.moduleStateHandler.requestStateChange(self.moduleStates.INITIALIZED.INTERFACE)

        # To-do: check whether State change has been made and state is actually running without errors If not,
        # go back to previous state

    def _clickedBtnStopRecorder(self):
        """ btnStopRecorder clicked. """
        print('Pressed Stop')
        self.moduleStateHandler.requestStateChange(self.moduleStates.ERROR)

        # set current data file name
        # self.lblDataFilename.setText('< none >')
    '''

    '''
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
    '''