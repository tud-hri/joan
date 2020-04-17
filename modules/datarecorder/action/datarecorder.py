from process import Control
from modules.datarecorder.action.datawriter import DataWriter
from datetime import datetime


class DatarecorderAction(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.module_states = None
        self.module_state_handler = None
        self.datarecorder_settings = None
        try:
            state_package = self.get_module_state_package(
                module='modules.datarecorder.widget.datarecorder.DatarecorderWidget')
            self.module_states = state_package['module_states']
            self.module_state_handler = state_package['module_state_handler']
            self.datarecorder_settings = self.get_module_settings(module='modules.datarecorder.widget.datarecorder.DatarecorderWidget')
        except Exception:
            pass
        self.filename = ''
        self.data_writer = DataWriter(news=self.get_all_news(), channels=self.get_available_news_channels(), settings_object=self.datarecorder_settings)

    def initialize(self):
        self.filename = self._create_filename(extension='csv')
        return True

    def write(self):
        now = datetime.now()
        self.data_writer.write(timestamp=now, news=self.get_all_news(), channels=self.get_available_news_channels())

    def stop(self):
        print('close the threaded file_handle(s)')
        self.data_writer.close()

    def start(self):
        self.data_writer.open(filename=self.get_filename())

    def _create_filename(self, extension=''):
        now = datetime.now()
        now_string = now.strftime('%Y%m%d_%H%M%S')
        filename = '%s_%s' % ('data', now_string)
        if extension != '':
            extension = extension[0] == '.' or '.%s' % extension
            filename = '%s%s' % (filename, extension)
        return filename

    def get_filename(self):
        return self.filename
