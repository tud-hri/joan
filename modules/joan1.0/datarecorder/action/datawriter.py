"""
Data, coming from the class News, is gathered regularly
The output is a comma-delimited csv file
A settingsfile is used to filter which data will be written
"""
import threading
import io
import csv
import os
from pathlib import Path

from modules.joanmodules import JOANModules

class DataWriter(threading.Thread):
    """
    Class DataWriter inherits the Thread class
    Writes data from modules to a file in a comma separated values format
    """
    def __init__(self, news=None, channels=[], settings=None):
        """
        :param news: contains news from modules (=channels)
        :param channels: are actually the keys to identify a module
        :param settings: contains all news-keys with a boolean to write or not to write, that's the question
        """
        threading.Thread.__init__(self)

        self.file_handle = None
        self.dict_writer = None
        self.news = news
        self.channels = channels
        self.fieldnames = []
        self.settings = settings

    def run(self):
        """
        Overridden from the thread class
        """
        pass
        #print('DataWriter runs in a thread:', self.is_alive())

    def recursive_filter_row(self, current_allow, current_data, row_name, row_names={}):
        """
        Go through the settings and through the news as they use the same keys
        Returns only news that is not 'censored'
        :param current_allow: is a dictionary from the settings variables to save within a module
        :param current_data: is a dictionary from the news within a module
        :param row_name: recursively concatenated key-name
        :return: a list of dictionaries with recursively concatenated keys and the corresponding values
        """
        if isinstance(current_allow, dict):
            for _key, _value in current_allow.items():
                if _value is True:
                    row_names['%s.%s' % (row_name, _key)] = current_data.get(_key)
                    #row_name = row_name.split('.')[:-1]
                else:
                    self.recursive_filter_row(current_allow.get(_key), current_data.get(_key), '%s.%s' % (row_name, _key), row_names)
            row_names_list = []
            for _key, _value in row_names.items():
                row_names_list.append({_key: _value})
            return row_names_list
        return ''

    def filter_first_row(self):
        """
        Creates the first column of the header row with the name 'time'
        Adds a recursively concatenated key to a list if it passes the filter
        :return: a list of recursively concatenated keys which passes a filter
        """
        row = ['time']
        header_list = []
        for channel in self.channels:
            latest_news = self.news[channel]
            readable_key = str(JOANModules(channel))

            result = self.recursive_filter_row(self.settings.variables_to_save.get(readable_key), 
                                               latest_news,
                                               readable_key)

            for news_items in result:
                for key in news_items.keys():
                    header_list.append(key)
        header_list = sorted(list(set(header_list)))
        return row + header_list

    def filter_row(self, news=None, channels=[]):
        """
        Creates the first column of a data-row with the current time
        Data which passes the filter will be added to the row where the column is defined by the recursively concatenated key
        :param news: contains news from modules (=channels)
        :param channels: are actually the keys to identify a module
        :return: a dictionaries of all news items from all channels (=modules) with recursively concatenated keys and the corresponding values
        """
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

    def open(self, filename, filepath='.', buffersize=io.DEFAULT_BUFFER_SIZE):
        """
        Opens a buffered file and with a headerline
        :param filepath: if specified, log files are saved in a directory
        :param filename: is the name of the file
        :param buffersize: is the size of the buffer for writing
        """
        # check if folder exists
        _path = Path(filepath)
        if not Path(filepath).exists():
            try:
                _path.mkdir(mode=0o777, parents=True)
            except FileExistsError:
                pass

        _fieldnames = self.filter_first_row()

        # open file and write the first row
        self.file_handle = open(os.path.join(filepath, filename), 'w', buffering=buffersize, newline='')
        self.dict_writer = csv.DictWriter(self.file_handle, fieldnames=_fieldnames)
        self.dict_writer.writeheader()

    def close(self):
        """
        Closes the filehandle
        """
        try:
            self.file_handle.close()
        except AttributeError:
            pass

    def write(self, timestamp=None, news=None, channels=[]):
        """
        Writes a row (=csv line) of news to the bottom of the outputfile
        :param timestamp: is the time when the news from a module is send to be published in the outputfile
        :param news: contains news from modules (=channels)
        :param channels: are actually the keys to identify a module
        """
        row = {}
        # row['time'] = timestamp.strftime('%H%M%S%f')  # had jumps in the time vector
        row['time'] = timestamp

        row.update(self.filter_row(news=news, channels=channels))
        self.dict_writer.writerow(row)
