import threading
import io
import csv
import copy
from modules.joanmodules import JOANModules

class DataWriter(threading.Thread):
    def __init__(self, news=None, channels=[], settings=None):
        threading.Thread.__init__(self)
        self.file_handle = None
        self.dict_writer = None
        self.news = news
        self.channels = channels

        self.fieldnames = []
        self.settings = settings
        self.settings_dict = {}

    def run(self):
        print(self.is_alive())

    def filter_first_row(self):
        # define first row, the headers for the columns
        # channel is a JOANModule object
        # news uses JOANModule object as key
        # self.settings.variables_to_save used str(JOANModules(channel)) as key
        row = ['time']
        for channel in self.channels:
            latest_news = self.news[channel]
            readable_key = str(JOANModules(channel))

            #element = copy.deepcopy(self.settings.variables_to_save)
            #element = element.get(readable_key)

            for key in latest_news.keys():
                if self.settings.variables_to_save[readable_key][key] is True:
                    #row.append('%s.%s' % (channel.split('.')[1], key))
                    row.append('%s.%s' % (readable_key, key))
                else:
                    for subkey in latest_news[key].keys():
                        if self.settings.variables_to_save[readable_key][key][subkey] is True:
                            #row.append('%s.%s' % (channel.split('.')[1], key))
                            row.append('%s.%s.%s' % (readable_key, key, subkey))

        self.columnnames(row)

    def filter_row(self, news=None, channels=[]):
        # define data rows, the content of the columns
        # channel is a JOANModule object
        # news uses JOANModule object as key
        # self.settings.variables_to_save used str(JOANModules(channel)) as key
        row = {}
        for channel in channels:
            latest_news = self.news[channel]
            readable_key = str(JOANModules(channel))

            for key in latest_news.keys():
                if self.settings.variables_to_save[readable_key][key] is True:
                    #row.append('%s.%s' % (channel.split('.')[1], key))
                    row.update({'%s.%s' % (readable_key, key): latest_news[key]})
                    #row.append('%s.%s' % (readable_key, key))
                else:
                    for subkey in latest_news[key].keys():
                        if self.settings.variables_to_save[readable_key][key][subkey] is True:
                            #row.append('%s.%s' % (channel.split('.')[1], key))
                            row.update({'%s.%s.%s' % (readable_key, key, subkey): latest_news[key][subkey]})

            #for key in latest_news:
            #    if self.settings.variables_to_save[readable_key][key] is True:
            #        #row.update({'%s.%s' % (channel.split('.')[1], key): latest_news[key]})
            #        row.update({'%s.%s' % (readable_key, key): latest_news[key]})
        return row

    def columnnames(self, keys=[]):
        # filters keys you want from the data and put them as header in the csv file
        self.fieldnames = keys

    def get_first_row(self):
        return self.fieldnames

    def open(self, filename, buffersize=io.DEFAULT_BUFFER_SIZE):
        # renew settings
        self.settings_dict = self.settings

        self.filter_first_row()

        # open file and write the first row
        self.file_handle = open(filename, 'w', buffering=buffersize, newline='')
        self.dict_writer = csv.DictWriter(self.file_handle, fieldnames=self.get_first_row())
        self.dict_writer.writeheader()

    def close(self):
        try:
            self.file_handle.close()
        except AttributeError:
            pass

    def write(self, timestamp=None, news=None, channels=[]):
        # get ALL news here, filter in self.filter and write
        # this class is a thread, so the main thread should continue while filtering and writing
        time = timestamp.strftime('%H%M%S%f')
        row = {}
        row['time'] = time  # datetime.now()

        row.update(self.filter_row(news=news, channels=channels))
        self.dict_writer.writerow(row)
