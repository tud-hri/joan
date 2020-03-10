""" Recorder for all the signal data.

See DESCRIPTION for a more detailed description if the format.
The signal data is stored simply as a series of float64 numbers. When
training starts, the file is opened and the header is written. Then new
data is added as it becomes available via the global buffering probe. This
means that in the event that the application crashes, little data is lost.
When the training is stopped, a finalizer is written to the file (so it
can be detected that the data is complete) and the file is closed.

Remarks:
  * The sample time of the data is currentlty the same as it is produced
    by the global sampling probe. Currently this is 100Hz.
  * The data is stored in little endian byte order.
  * The data is uncompressed. Although compression would reduce the file
    size, it means additional complexity. With zlib compression (which Matlab
    supports via Java) we can reduce the file size to ~70%. This does not
    seem worth the effort.

Memory:
  * With 50 signals of 8 bytes, we obtain 400 bytes per time instance
  * With 100Hz, this corresponds to 39KB/s or 2.3MB/minute
  * Storing data for a patient with 50 sessions of 10 minutes: 1.1GB
  * Having 1000 such patients: 1TB
  * That does not seem too hard to handle :)

"""

import os, sys, time
import datetime
import pyzolib.ssdf as ssdf
import numpy as np
import struct
import ctypes

DESCRIPTION = """
HAPTIC TRAINER SIGNAL DATA LOG
File format: SSDF header with a binary body
Header fields:
    map: list of strings with the names of the signals    
    time: string with start time of the log, HH:MM:SS
    date: string with start date of the log, YYYY-MM-DD
    sampleTime: sample time of the data
Separator: 
    80 '=' characters followed by a linefeed character.
Data:
    Blob of 64 bit floating point numbers (little endian). Each "row"
    of numbers reprsents all signal at one timestamp. Each row contains
    N numbers, where N is len(header.map).
Finalizer: 
    File is finalized with a linefeed character if closed in a nice way.
""".lstrip()


class SignalRecorder:
    """
    This logger logs the data produced by the buffering probe. It has an
    ssdf header, but the data is stored in binary form (little endian).
    
    Does not inherit from BaseRecorder, because it differs quite a bit
    from the other two formats, since the signal recorder stores to binary 
    format.
    
    """
    def __init__(self, haptictrainer):
        # It could be that the lopesInterface does not have a parametersProxy
        # yet, so just store a reference and connect to the parameters when
        # startup is complete.
        self._haptictrainer = haptictrainer
        self._interface = haptictrainer.interface
        self._probeSignalKeys = None
        self._addParamsKeys = []
        self._addParams = dict()
        self._numSignals = None
        self._logfile = None
        self._logStartTime = None
        self._pointertypes = dict()

        #self._interface.callWhenStartupCompleted(self._connectToParameters)
        self._interface.startupCompleted.connect(self._connectToParameters)
    
    def _connectToParameters(self):
        # Called when haptic trainer initialization is done
        assert self._logfile is None # Cannot connect while logging 
        
        self._probeSignalKeys = self._interface.samplingProbe.keys
        
        # connect signal recorder to sampling probe hasData signal     
        self._interface.samplingProbe.hasData.connect(self._onNewData)
    
        # add custom parameters (other than the ones we collect from the interface.
        # This includes parameters you calculate in the experiment, etc, etc.
        # had to be pointer!
        self.addParameter("state", self._haptictrainer.statehandler.state_c_int)

        # parameters from task
        self.addParameter("tasktime", self._haptictrainer.experiment.trial.task.tasktime_msec_c_float)
        self.addParameter("xtarget",  self._haptictrainer.experiment.trial.task.xtarget_c_float)
        self.addParameter("ytarget",  self._haptictrainer.experiment.trial.task.ytarget_c_float)
        self.addParameter("ztarget",  self._haptictrainer.experiment.trial.task.ztarget_c_float)

    
    def addParameter(self, name, param):
        """ Add signals to be logged with each time step (of the probe). 
        Right now I am storing the ref of the signal, so we can read out it's value at any time we want (at each _onNewData call."""

        if isinstance(param, (ctypes.c_float, ctypes.c_int)):
            # check if the parameterName is already in the list
            if not name in self._addParamsKeys:
                self._addParamsKeys += [name] # add key to list
                self._addParams[name] = param
        else:
            raise TypeError('Parameter ', name,' needs to be a ctypes.c_float or ctypes.c_int')
    
    def _onNewData(self, data):
        """ Log the incoming data
        data is a dict wich has for each key/signal a numpy array.
        We stack these 1D arrays in a 2D array, one column for each signal.
        Then we write the array. Because we use 'C' arrays, the data
        is written per row.
        """

        if self._logfile:
        # write bytes
            # Initialize array
            N = len(self._probeSignalKeys) + len(self._addParamsKeys)
            M = data['time'].size
            dataArray = np.empty((M, N), np.float64, 'C')

            # Add extra parameters to data array
            for i, key in enumerate(self._addParamsKeys):
                value = self._addParams[key].value # this dict has ctypes
                data[key] = value*np.ones((M,))

            # all parameter keys
            allKeys = self._probeSignalKeys + self._addParamsKeys

            # Stack signal data
            for i, key in enumerate(allKeys):
                dataArray[:, i] = data[key]

            # Write
            if sys.byteorder != 'little':
                dataArray.byteswap(True) # Inplace byteswap

            self._logfile.write(dataArray.tobytes())

    def start(self, logfile, starttime, starttime_gui=None):
        """
        Start the logging to a file
        
        logfile: file-like object which has a write() and a close() method
        starttime: the current time (in seconds) ('wallclocktime')
        starttime_gui: a datetime.datetime object giving the start time at the
          GUI PC (if omitted or None, the current time is used)
          
        """
        # Assert that we are initialized
        assert(self._probeSignalKeys is not None) 
        
        # Create time object if needed
        if starttime_gui is None:
            starttime_gui = datetime.datetime.now()

        # Build header as SSDF struct
        header = ssdf.Struct()
        header.map = self._probeSignalKeys + self._addParamsKeys
        header.time = starttime_gui.strftime('%H%M%S')
        header.date = starttime_gui.strftime('%Y%m%d')
        header.sampleTime = self._interface.samplingProbe.sampleTime

        # Write comment, header and separator
        for line in DESCRIPTION.splitlines():
            logfile.write('# %s\n'%line)

        logfile.write(ssdf.saves(header))
        logfile.write('\n%s\n' % ('='*80))
        #self._logStartTime = float(starttime_gui)
        self._logfile = logfile

    def stop(self, endtime_hlc, isError):
        """
        Write the footer of the logfile, and close the logfile
        """

        # wait for threadedfilewriter to finish
        self._logfile.write('\n') # If this is present, the logfile was nicely closed
        self._logfile.close()
        self._logfile = None
        print "stop recorder"


def readSignalRecording(filename):
    """
    Read a signal recording. Returns a dict that maps signal keys to 1D numpy
    arrays.
    
    """
    
    # Open file
    f = open(filename, 'rb')
    
    # Define separtor
    t1 = ('='*40).encode('ascii')
    t2 = '\n'.encode('ascii')
    separatorPos = 0
    
    # Seek separator 
    while True:
        test = f.read(40)
        if not test:
            break
        elif test == t1:
            separatorPos = 0
            for i in range(41):
                test = f.read(1)
                if test == t1[:1]:
                    continue
                elif test == t2:
                    separatorPos = f.tell()
                else:
                    break
            if separatorPos:
                break
    
    # Check
    if not separatorPos:
        raise RuntimeError('Could not find separator.')
    else:
        separatorPos1, separatorPos2 = separatorPos - 81, separatorPos
    
    # Read header
    f.seek(0)
    header = ssdf.loads(f.read(separatorPos1).decode('utf-8'))
    
    # Read remaining data
    f.seek(separatorPos2)
    data = f.read()
    f.close()
    
    # Check size that we need for arrays
    N = len(header.map)
    M = len(data) // (N*8)
    
    # Make numpy array
    a = np.frombuffer(data, np.float64, count=N*M)
    a.shape = M, N
    
    # Check what's left, and check last element
    numberOfExtraElements = len(data) - N*M*8
    lastCharIsLineFeed = data[-1:] == b'\n'
    if numberOfExtraElements != 1:
        print('Warning: Data looks incomplete: footer is not 1 element but %i' % numberOfExtraElements)
    elif not lastCharIsLineFeed:
        print('Warning: Data looks incomplete: footer is not a newline but %r' % data[-1:])
    
    # Make dict, return
    dataDict = {}
    for i, key in enumerate(header.map):
        dataDict[key]  = a[:, i]
    return dataDict

def getFirstSampleWallClockTimeFromSignalsFile(filename):
    """
    Returns the r.cont.wallClockTime entry for the first sample in the signals-file.
    This is needed for correcting for a bug in the .params-file timestamps (prior to
    changing the format on 140627). If it didn't work (e.g. because there were no
    samples or because the 'r.cont.wallClockTime' was not found), a RuntimeError or ValueError is raised.
    """
    # Open file
    f = open(filename, 'rb')
    # Define separtor
    t1 = ('='*40).encode('ascii')
    t2 = '\n'.encode('ascii')
    separatorPos = 0
    # Seek separator 
    while True:
        test = f.read(40)
        if not test:
            break
        elif test == t1:
            separatorPos = 0
            for i in range(41):
                test = f.read(1)
                if test == t1[:1]:
                    continue
                elif test == t2:
                    separatorPos = f.tell()
                else:
                    break
            if separatorPos:
                break
    
    # Check
    if not separatorPos:
        raise RuntimeError('Could not find separator.')
    else:
        separatorPos1, separatorPos2 = separatorPos - 81, separatorPos
    
    # Read header
    f.seek(0)
    header = ssdf.loads(f.read(separatorPos1).decode('utf-8'))
    
    # The wallClockTime is at position separaterPos2 + 8*indexOfWallClockTime
    # So go there and read 8 bytes. If less than 8 bytes were read, this implies
    # that there were no samples at all. In that case, raise a RuntimeError.
    f.seek (separatorPos2 + 8 * header.map.index('r.cont.wallClockTime'))
    data = f.read( 8 )
    if len(data)!=8:
        raise RuntimeError("No data in .signalsfile.")
    f.close()
    
    wallClockTime = struct.unpack("<d", data)[0]
    return wallClockTime

# if False: # Set to True to do this test
#     #fname = r'C:\almar\projects\py2\lopes\testdata\patients\1 Reilink, Rob (6-10-1983)\recordings\20121128_170233.signals'
#     fname = r'C:\almar\projects\py2\lopes\testdata\patients\2 Klein, Almar (4-5-1983)\recordings\20121129_111839.signals'
#     data = readSignalRecording(fname)
#     import visvis as vv
#     vv.figure(10); vv.clf()
#     vv.plot(data['time'], data['r.cont.jointAngles.RHA'])


