from process import Control
from modules.datarecorder.action.datawriter import DataWriter
from datetime import datetime


class DatarecorderAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.moduleStates = None
        self.moduleStateHandler = None
        self.datarecorderSettings = None
        try:
            statePackage = self.getModuleStatePackage(
                module='modules.datarecorder.widget.datarecorder.DatarecorderWidget')
            self.moduleStates = statePackage['moduleStates']
            self.moduleStateHandler = statePackage['moduleStateHandler']
            self.datarecorderSettings = self.getModuleSettings(module='modules.datarecorder.widget.datarecorder.DatarecorderWidget')
        except Exception:
            pass
        self.filename = ''
        self.dataWriter = DataWriter(news=self.getAllNews(), channels=self.getAvailableNewsChannels(), settingsObject=self.datarecorderSettings)

    def initialize(self):
        self.filename = self._createFilename(extension='csv')
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
        now = datetime.now()
        nowString = now.strftime('%Y%m%d_%H%M%S')
        filename = '%s_%s' % ('data', nowString)
        if extension != '':
            extension = extension[0] == '.' or '.%s' % extension
            filename = '%s%s' % (filename, extension)
        return filename

    def getFilename(self):
        return self.filename
