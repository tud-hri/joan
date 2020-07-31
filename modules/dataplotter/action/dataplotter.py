"""
Data, coming from the class News, is gathered regularly
The output is shown in a separate window
A settingsfile is used to filter which data will be plotted
"""
import json
import threading
import sys  # TODO remove this when testing is done
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from plotwindow import PlotWindow
#from modules.joanmodules import JOANModules

class DataPlotter(threading.Thread):
    """
    Class DataPlotter inherits the Thread class
    Puts data from modules on plot-window(s)
    """

    def __init__(self, news=None, channels=[], settings=None):
        """
        :param news: contains news from modules (=channels)
        :param channels: are actually the keys to identify a module
        :param settings: contains all news-keys with their plot properties
        """
        threading.Thread.__init__(self)

        self.news = news
        self.channels = channels
        self.fieldnames = []
        self.settings = settings

        # plot stuff
        self.plot_item = {}  # holds the plot items for each plot
        self.plot_item_data = {}  # holds the data for each plot item
        self.plot_item_data_properties = {}  # holds the data properties for each plot item

        self.x = [0, 100]
        self.y = [50, 50]

        # for testing
        self.sign = 1
        self.counter = 0
        # end testing


        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()


        self.set_window()
        self._get_plot_widgets(json.loads(test_settings))


    def set_window(self):
        plot_window_instance = PlotWindow()
        self.plot_window = plot_window_instance.get_plot_window()
        

        self.graph_layout = pg.GraphicsLayoutWidget()

        #self.graph_layout = pg.PlotWidget()
        self.plot_window.setCentralWidget(self.graph_layout)
        self.plot_window.show()


    def _get_plot_widgets(self, settings):
        available_plot_list = settings.get("Data Plotter").get("picklist_plot_windows")
        settings_string = json.dumps(settings.get("Data Plotter").get("variables_to_save"))

        print(available_plot_list)
        print(settings_string)

        
        for plot in range(0, len(available_plot_list)):
            if available_plot_list[plot] != 'No':
                if settings_string.count('"plot_window": "%s"' % available_plot_list[plot]) > 0:
                    self.plot_item[available_plot_list[plot]] = pg.PlotItem(title=available_plot_list[plot])
                    self.plot_item_data[available_plot_list[plot]] = None
                    self.plot_item_data_properties[available_plot_list[plot]] = {}

        print(self.plot_item)
        self.plot_item["plot 1"].setYRange(0, 100, padding=0)
        self.plot_item["plot 2"].setYRange(0, 100, padding=0)

        self.plot_item_data_properties["plot 1"]["line_color"] = "#000000"
        self.plot_item_data_properties["plot 1"]["line_type"] = "solid"
        self.plot_item_data_properties["plot 2"]["line_color"] = "#ff0000"
        self.plot_item_data_properties["plot 2"]["line_type"] = "dashed"

        pen = pg.mkPen({"color": self.plot_item_data_properties["plot 1"]["line_color"],
                        "style":  QtCore.Qt.SolidLine})


        self.graph_layout.addItem(self.plot_item["plot 1"], row=0, col=0)
        self.graph_layout.addItem(self.plot_item["plot 2"], row=1, col=0)
        self.graph_layout.setBackground('w')

        self.plot_item_data["plot 1"] = self.plot_item["plot 1"].plot(self.x, self.y, pen=pen)

        pen = pg.mkPen({"color": self.plot_item_data_properties["plot 2"]["line_color"],
                        "style":  QtCore.Qt.DashLine})
        self.plot_item_data["plot 2"] = self.plot_item["plot 2"].plot(self.x, self.y, pen=pen)
         
    def update_plot_data(self, timestamp=None, news=None, channels=[]):
        """
        Updates the plot data
        """
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        if self.y[-1] < 8 and self.sign < 0:
            self.sign = self.sign * -1
        if self.y[-1] > 85 and self.sign > 0:
            self.sign = self.sign * -1
        self.counter += self.sign * 2
        self.y = self.y[1:]  # Remove the first

        self.y.append(self.counter)

        self.plot_item_data["plot 1"].setData(y=self.y, x=self.x)
        self.plot_item_data["plot 2"].setData(y=self.y, x=self.x)

    def run(self):
        """
        Overridden from the thread class
        """
        pass
        #print('DataPlotter runs in a thread:', self.is_alive())

    def recursive_filter_row(self, current_allow, current_data, row_name):
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

    def write(self, timestamp=None, news=None, channels=[]):
        """
        Writes a row (=csv line) of news to the bottom of the outputfile
        :param timestamp: is the time when the news from a module is send to be published in the outputfile
        :param news: contains news from modules (=channels)
        :param channels: are actually the keys to identify a module
        """
        row = {}
        row['time'] = timestamp.strftime('%H%M%S%f')

        row.update(self.filter_row(news=news, channels=channels))
        self.dict_writer.writerow(row)


test_settings = '''{
    "Data Plotter": {
        "picklist_line_colors": [
            "blue",
            "#000000"
        ],
        "picklist_line_types": [
            "solid",
            "dashed",
            "dotted"
        ],
        "picklist_plot_windows": [
            "No",
            "plot 1",
            "plot 2",
            "plot 3",
            "plot 4"
        ],
        "variables_to_save": {
            "Agent Manager": {
                "agents": {},
                "connected": {
                    "line_color": "blue",
                    "line_type": "solid",
                    "plot_window": "plot 2"
                }
            },
            "Data Plotter": {},
            "Data Recorder": {},
            "Hardware Manager": {},
            "Steering Wheel Controller Manager": {},
            "Template": {
                "datawriter output": {
                    "line_color": "blue",
                    "line_type": "dashed",
                    "plot_window": "plot 1"
                }
            }
        },
        "write_interval": 5
    }
}
'''

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    data_plotter = DataPlotter()

    sys.exit(app.exec_())
