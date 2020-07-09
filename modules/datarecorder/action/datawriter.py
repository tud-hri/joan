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

    def recursive_filter_row(self, current_allow, current_data, row_name):
        if isinstance(current_allow, dict):
            for _key, _value in current_allow.items():
                if isinstance(_value, dict):
                    row_name = '%s.%s' % (row_name, _key)
                    return self.recursive_filter_row(current_allow.get(_key), current_data.get(_key), row_name)
                else:
                    row_names = []
                    for deepest_key in current_allow.keys():
                        if current_allow.get(deepest_key) is True:
                            deepest_row_name = '%s.%s' % (row_name, deepest_key)
                            row_names.append({deepest_row_name: current_data.get(deepest_key)})
                    return row_names
            return ''


    def filter_first_row(self):
        # define first row, the headers for the columns
        # channel is a JOANModule object
        # news uses JOANModule object as key
        # self.settings.variables_to_save used str(JOANModules(channel)) as key
        row = ['time']
        for channel in self.channels:
            latest_news = self.news[channel]
            readable_key = str(JOANModules(channel))

            result = self.recursive_filter_row(self.settings.variables_to_save.get(readable_key), 
                                               latest_news,
                                               readable_key)

            for news_items in result:
                for key in news_items.keys():
                    row.append(key)

        self.columnnames(row)

    def filter_row(self, news=None, channels=[]):
        # define data rows, the content of the columns
        # channel is a JOANModule object
        # news is using JOANModule object as key
        # self.settings.variables_to_save is using str(JOANModules(channel)) as key
        row = {}
        for channel in channels:
            latest_news = self.news[channel]
            readable_key = str(JOANModules(channel))

            result = self.recursive_filter_row(self.settings.variables_to_save.get(readable_key), 
                                               latest_news,
                                               readable_key)

            for news_item in result:
                row.update(news_item)
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
