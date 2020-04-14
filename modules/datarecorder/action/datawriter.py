import threading
import io
import csv
from modules.datarecorder.action.datarecordersettings import DatarecorderSettings


class DataWriter(threading.Thread):
    def __init__(self, news=None, channels=[]):
        threading.Thread.__init__(self)
        self.filehandle = None
        self.dictWriter = None
        self.news = news
        self.channels = channels

        self.fieldnames = []
        self.datarecorderSettings = DatarecorderSettings()
        self.settings = None

    def run(self):
        print(self.is_alive())

    def filterFirstRow(self, news=None, channels=[]):
        # define first row, the headers for the columns
        row = ['time']
        for channel in self.channels:
            latestNews = self.news[channel]
            for key in latestNews:
                if self.settings['modules'][channel][key] is True:
                    row.append('%s.%s' % (channel.split('.')[1], key))
        self.columnnames(row)
        print('first', row)

    def filterRow(self, news=None, channels=[]):
        row = {}
        for channel in channels:
            latestNews = news[channel]
            for key in latestNews:
                if self.settings['modules'][channel][key] is True:
                    row.update({'%s.%s' % (channel.split('.')[1], key): latestNews[key]})
        return row

    def columnnames(self, keys=[]):
        # filters keys you want from the data and put them as header in the csv file
        self.fieldnames = keys

    def getFirstRow(self):
        return self.fieldnames

    def open(self, filename, buffersize=io.DEFAULT_BUFFER_SIZE):
        # renew settings
        self.settings = self.datarecorderSettings.read()
        self.filterFirstRow()

        # open file and write the first row
        print('buffersize', buffersize)
        self.filehandle = open(filename, 'w', buffering=buffersize, newline='')
        self.dictWriter = csv.DictWriter(self.filehandle, fieldnames=self.getFirstRow())
        self.dictWriter.writeheader()

    def close(self):
        self.filehandle.close()

    def write(self, timestamp=None, news=None, channels=[]):
        # get ALL news here, filter in self.filter and write
        # this class is a thread, so the main thread should continue while filtering and writing
        time = timestamp.strftime('%H%M%S%f')
        row = {}
        row['time'] = time  # datetime.now()

        row.update(self.filterRow(news=news, channels=channels))
        self.dictWriter.writerow(row)
