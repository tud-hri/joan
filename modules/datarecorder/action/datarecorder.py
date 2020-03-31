from process import Control
from PyQt5 import QtCore
import io
from modules.datarecorder.action.datawriter import DataWriter
from datetime import datetime
#from modules.steeringcommunication.widget.steeringcommunication import SteeringcommunicationWidget

class DatarecorderAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.moduleStates = None
        self.moduleStateHandler = None
        try:
            statePackage = self.getModuleStatePackage(module='module.datarecorder.widget.daterecorder.DatarecorderWidget')
            self.moduleStates = statePackage['moduleStates']
            self.moduleStateHandler = statePackage['moduleStateHandler']
        except:
            pass
        self.filename = ''
        self.dataWriter = DataWriter(news=self.getAllNews(), channels=self.getAvailableNewsChannels())

    def initialize(self):
        print('Initialize in action/datarecorder')
        self.filename = self._createFilename(extension='csv')
        print(self.filename)


        #filename = "test.csv"

        #fieldnamesSteeringcommunication = ['time', 'throttle', 'damping']
        #fieldnamesSteeringcommunication.extend(SteeringcommunicationWidget.data.keys())
        # = ['first_name', 'last_name']
        #print('fieldnamesSteeringcommunication', fieldnamesSteeringcommunication)
        #fieldnames.insert(0, 'time')

        #self.dataWriter.filteredRow = 
        #self.dataWriter.columnnames(fieldnamesSteeringcommunication)
        #self.dataWriter.open(filename=self.filename, buffersize=io.DEFAULT_BUFFER_SIZE)
        #self.dataWriter.start()

        # search for filename
        # create threaded filehandler(s)
        return True

    def write(self):
        now = datetime.now()
        self.dataWriter.write(timestamp=now, news=self.getAllNews(), channels=self.getAvailableNewsChannels())   

    def stop(self):
        print('close the threaded filehandle(s)')
        self.dataWriter.close()

    def start(self):
        self.dataWriter.open(filename=self.getFilename())
    
    def _createFilename(self, extension=''):
        ##now = QtCore.QDateTime.currentDateTime()
        ##nowString = now.toString('yyyyMMdd_hhmmss')
        now = datetime.now()
        nowString = now.strftime('%Y%m%d_%H%M%S')
        filename = '%s_%s' % ('data', nowString)
        if extension != '':
            extension = extension[0] == '.' or '.%s' % extension
            filename = '%s%s' % (filename, extension)
        return filename

    def getFilename(self):
        return self.filename
    
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