"""
This module defines the DataRecorder. It controls the SignalRecorder (and others as well, if necessary)
"""

import os
import datetime
import ctypes

from util import QtCore, ThreadedFileWriter
from haptictrainer import STATES
from signalrecorder import SignalRecorder


class DataRecorder(QtCore.QObject):
    """
    The DataRecorder takes care of starting and stopping the
    individual SignalRecorder.
    It monitors the HapticTrainer state. When the STATES.RUNEXP
    state is entered, a recording is started, and when the state is
    left, the recording is stopped.
    
    When a recording is started, a unique filename is generated, and the
    appropriate recording files are created.
    """
    
    ## Signals
    recordingStarted = QtCore.Signal() #: Emitted when the current recording is started
    recordingFinished = QtCore.Signal() #: Emitted when the current recording is finished

    ## Properties
    @property
    def currentFilename(self):
        return self._currentFilename

    @property
    def initialized(self):
        return self._initialized

    @property
    def recordingdirectory(self, newdir):
        self._recordingDir = newdir

    ## Methods
    def __init__(self, haptictrainer):
        QtCore.QObject.__init__(self)
        self._active = False
        self._haptictrainer = haptictrainer
        self._currentFilename = ''

        self._recordingDir = ''
        self._subjectid = ''

        self._initialized = False

        self.recordStartAndStop = False
        # Default mode: record only the period between (but excluding) starting and stopping).
        # You can change this variable during run-time (at any time) to switch to recording including start and stop
                
        # Instantiate individual recorders
        self._signalRecorder = SignalRecorder(self._haptictrainer)

        # add parameters to signal recorder here
        #self._signalRecorder.addParameter("", ctypes.c_float)
        
        # Monitor Haptic Trainer state changes
        self._haptictrainer.statehandler.stateChanged.connect(self._onStateChanged)

    def initialize(self):
        """ initialize the data recorder, called when the user hits the initialize button in the widget. """

        # needs to be try/catch?

        # create directory
        # Make directory
        self._recordingDir = 'recordings'
        if not os.path.exists(self._recordingDir):
            os.makedirs(self._recordingDir)

        # set bool that initialization is done
        self._initialized = True

        # initialization done, request state change to STATES.INITIALIZED.DATARECORDER
        self._haptictrainer.statehandler.requestStateChange(STATES.INITIALIZED.DATARECORDER)

    def start(self, state):
        """
        Start a recording (stop previous one if one is already running)
        """
        self.stop() # Stop if we were already started

        try:
            # time
            now = datetime.datetime.now()

            timestamp = now.strftime('%Y%m%d_%H%M%S')

            # to do: prefix should include the subject number etc?
            prefix = 'data'
            if self._haptictrainer.experiment.trial.trialtype == 1:
                self._currentFilename = prefix + '_' + self._subjectid + '_' + self._findUniqueSuffix(self._recordingDir, timestamp) + '_' + 'Solo' + '.signals'
            if self._haptictrainer.experiment.trial.trialtype == 2:
                self._currentFilename = prefix + '_' + self._subjectid + '_' + self._findUniqueSuffix(self._recordingDir, timestamp) + '_' + 'Dual' + '.signals'

            # Start the individual recorders
            self._signalRecorder.start(ThreadedFileWriter(self._recordingDir + '/' + self._currentFilename), now, now)
            
            # we're active!
            self._active = True

            # and let everyone know!
            self.recordingStarted.emit()
             
        except Exception as e:
            raise RuntimeError('Error starting the datarecorder: ', e)
    
    def stop(self, isError=False):
        """
        Stop the current recording (do nothing if we were not recording)
        Input argument isError: set to False if no error occurred. If an error did occur, set it to True, or to a string representing the error.
        """
        if not self._active:
            return
        
        # time
        now = datetime.datetime.now()

        # Stop the individual recorders
        self._signalRecorder.stop(now, isError)
            
        self._active = False
        
        # recording finished, emit signal
        self.recordingFinished.emit()

    def _onStateChanged(self, state):
        """ This function is called when the state changes. It controls whether data is being recorded. """

        # retrieve subject id (if changed). Not an elegant way of doing this, but it works
        if state == STATES.EXPERIMENT.SUBJECTIDENTERED:
            self._subjectid = self._haptictrainer.gui.widgets["experimentwidget"].subjectid

        # start data recording
        if (state == STATES.EXPERIMENT.TRIAL.TASK) or \
                (state == STATES.DEBUG.DATARECORDER.START):  # add here all the states in which data recording should occur!
            if not self._active:
                self.start(state)  # start the data recorder!
        else:
            # now the staterecorder is always stopped if active and state is changed. Should work in operation.
            # Also in dev mode? Not sure
            if self._active:
                # check if an error occured. If so, add this to the data file
                if state in STATES.ERROR:
                    errorMessage = "error occured, stopping data recorder"
                else:
                    errorMessage = False

                # stop the data recorder
                self.stop(errorMessage)

    def _onSubjectIDEntered(self, sid):
        """ subject id entered, add to prefix"""
        self._subjectid = sid

    @staticmethod
    def _findUniqueSuffix(dir, basePrefix):
        """
        Create unique prefix for filenames. Check which files exist
        in the dir. The prefix starts with the basePrefix, then 
        _1, _2 etc is added if required to create a unique prefix
        """
        
        # Find which files exist in the dir
        existingFiles = os.listdir(dir)
        
        i = 0 # postfix _1, _2; 0 = no postfix
        while True:
            # Build prefix to be tried
            prefix = basePrefix + (('_' + str(i)) if i else '')
            
            # See if any files exist whose names start with prefix
            if not any([file.startswith(prefix) for file in existingFiles]):
                return prefix # We have found a suitable prefix
            i += 1 # Try next sequence number
