"""
Data, coming from the class News, is gathered regularly
The output is shown in a separate window
A settingsfile is used to filter which data will be plotted
"""
import math
import json
import threading
import sys  # TODO remove this when testing is done
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from modules.dataplotter.action.plotwindow import PlotWindow

from modules.joanmodules import JOANModules
from modules.dataplotter.action.dataplottersettings import PlotWindows
from modules.dataplotter.action.dataplottersettings import LineTypes
from modules.dataplotter.action.dataplottersettings import LineColors

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
        self.settings = settings

        # plot stuff
        self.plot_item = {}  # holds the plot items for each plot
        self.plot_item_data = {}  # holds the data for each plot item
        self.plot_item_data_properties = {}  # holds the data properties for each plot item

        self.plot_data_mapping = {}  # hold the mapping from str to enum-key

        self.x = {}  # for each plot
        self.y = {}  # for each plot
        self.range_min = {}  # for each plot window
        self.range_max = {}  # for each plot window

        # for testing
        self.sign = 1
        self.counter = 0
        # end testing

        '''
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        '''

        #self.set_window()

    def set_window(self):
        plot_window_instance = PlotWindow()
        self.plot_window = plot_window_instance.get_plot_window()

        self.graph_layout = pg.GraphicsLayoutWidget()
        self.plot_window.setCentralWidget(self.graph_layout)
        self.plot_window.show()
        self._get_plot_widgets()

        self.filter_row()

    def _get_plot_widgets(self):
        """
        Determine how many plotwindows are defined in the settings and create them
        """
        settings_string = json.dumps(self.settings.variables_to_save)

        for plot in PlotWindows:
        #for plot in self.settings.picklist_plot_windows:
            if plot not in (PlotWindows.NOPLOT, PlotWindows.KEY):
                if settings_string.count('"%s": "%s"' % (PlotWindows.KEY, plot)) > 0:
                    self.plot_item[plot] = pg.PlotItem(title=plot)
                    self.plot_item_data[plot] = None
                    self.plot_item_data_properties[plot] = {}

                    self.range_min[plot] = 0
                    self.range_max[plot] = 1

                    self.plot_data_mapping[str(PlotWindows.KEY)] = PlotWindows.KEY

                    # TODO: move this elsewhere to make this for every plotitem as defined by 'legenda' in data_plot
                    self.x[plot] = [0, 100]
                    self.y[plot] = [50, 50]


        # initialise plot windows so they can be updated with real data
        self.graph_layout.setBackground('w')
        grid_x = 0
        grid_y = 0
        max_x = int(math.sqrt(len(self.plot_item) + 1))
        for plot in self.plot_item:

            self.plot_item[plot].setYRange(self.range_min[plot], self.range_max[plot], padding=0)

            self.plot_item_data_properties[plot][LineColors.KEY] = LineColors.color(LineColors.BLACK)
            self.plot_item_data_properties[plot][LineTypes.KEY] = LineTypes.view(LineTypes.SOLID)

            pen = pg.mkPen({"color": self.plot_item_data_properties[plot][LineColors.KEY],
                            "style":  self.plot_item_data_properties[plot][LineTypes.KEY]
                            })

            # grid arrangement, depending on the number of plots
            # TODO: check if this is correct
            self.graph_layout.addItem(self.plot_item[plot], row=grid_y, col=grid_x)
            grid_x += 1
            if grid_x > max_x:
                grid_x = 0
                grid_y += 1

            self.plot_item_data[plot] = self.plot_item[plot].plot(self.x[plot], self.y[plot], pen=pen)

         
    def update_plot_data(self, plot_data):
        """
        TODO: maak passend commentaar
        Updates the plot data
        """
        '''
        plot_data: {'time': '150619055458', 
        <PlotWindows.PLOT2: 2>: {'line_color': 'zwart', 
                                'line_type': 'solid', 
                                'plot_window': 'Plot 2', 
                                'legenda': 'Template.datawriter output', 
                                'value': 2020}}
        '''
        # TODO: get x-as from timestamp

        for plot in self.plot_item:

            if plot_data.get(plot):
                # TODO make x and y for row-identifier as defined in 'legenda' in plot_data
                self.x[plot] = self.x[plot][1:]  # Remove the first y element.
                self.x[plot].append(self.x[plot][-1] + 1)  # Add a new value 1 higher than the last.

                lc =  plot_data.get(plot).get(str(LineColors.KEY))
                lc_enum_value = LineColors.reverse(lc).value

                lt = plot_data.get(plot).get(str(LineTypes.KEY))
                lt_enum_value = LineTypes.reverse(lt).value

                self.plot_item_data_properties[plot][LineColors.KEY] = LineColors.color(LineColors(lc_enum_value))
                self.plot_item_data_properties[plot][LineTypes.KEY] = LineTypes.view(LineTypes(lt_enum_value))
                pen = pg.mkPen({"color": self.plot_item_data_properties[plot][LineColors.KEY],
                                "style":  self.plot_item_data_properties[plot][LineTypes.KEY]
                                })

                self.y[plot] = self.y[plot][1:]  # Remove the first TODO, make this per item as defined in 'legenda'
                self.y[plot].append(plot_data.get(plot).get('value'))

                if plot_data.get(plot).get('value') < self.range_min[plot]:
                    self.range_min[plot] = plot_data.get(plot).get('value')
                    self.plot_item[plot].setYRange(self.range_min[plot], self.range_max[plot], padding=0)

                if plot_data.get(plot).get('value') > self.range_max[plot]:
                    self.range_max[plot] = plot_data.get(plot).get('value')
                    self.plot_item[plot].setYRange(self.range_min[plot], self.range_max[plot], padding=0)

                self.plot_item_data[plot].setData(y=self.y[plot], x=self.x[plot], pen=pen)
          
    def run(self):
        """
        Overridden from the thread class
        """
        pass
        #print('DataPlotter runs in a thread:', self.is_alive())

    def _recursive_filter_row(self, current_allow, current_data, row_name):
        """
        TODO: maak passend commentaar
        Go through the settings and through the news as they use the same keys
        Returns only news that has a plot_window defined
        :param current_allow: is a dictionary from the settings variables to save within a module
        :param current_data: is a dictionary from the news within a module
        :param row_name: recursively concatenated key-name
        :return: a list of dictionaries with recursively concatenated keys and the corresponding values
        """
        if isinstance(current_allow, dict):
            for _key, _value in current_allow.items():
                if isinstance(_value, dict):
                    for sub_key, sub_value in _value.items():
                        if isinstance(sub_value, dict):
        
                            row_name = '%s.%s' % (row_name, _key)
                            return self._recursive_filter_row(current_allow.get(_key), current_data.get(_key), row_name)
                        else:
                            row_names = []
                            for deepest_key in current_allow.keys():
                                print("%s - %s - %s" % ("hier kan ik wat mee!", deepest_key, current_allow.get(deepest_key)))
                                print ('b b b', self.plot_item, type(current_allow.get(deepest_key)) )

                                if current_allow.get(deepest_key) != {}:
                                    for plot in self.plot_item:

                                        if str(plot) == current_allow.get(deepest_key).get(str(PlotWindows.KEY)):
                                            deepest_row_name = '%s.%s' % (row_name, deepest_key)
                                            if str(current_data.get(deepest_key)).isnumeric():
                                                current_allow.get(deepest_key).update({'legenda': deepest_row_name, 'value': current_data.get(deepest_key)})
                                                row_names.append({plot: current_allow.get(deepest_key)})
                            return row_names
            return ''

    def filter_row(self, news=None, channels=[]):
        """
        TODO: maak passend commentaar
        Creates the first column of a data-row with the current time
        Data which passes the filter will be added to the row where the column is defined by the recursively concatenated key
        :param news: contains news from modules (=channels)
        :param channels: are actually the keys to identify a module
        :return: a dictionaries of all news items from all channels (=modules) with recursively concatenated keys and the corresponding values
        """
        row = {}
        for channel in self.channels:
            latest_news = self.news[channel]
            readable_key = str(JOANModules(channel))

            result = self._recursive_filter_row(self.settings.variables_to_save.get(readable_key),
                                                latest_news,
                                                readable_key)

            for news_item in result:
                row.update(news_item)
        return row

    def write(self, timestamp=None, news=None, channels=[]):
        """
        TODO: maak passend commentaar
        Writes a row (=csv line) of news to the bottom of the outputfile
        :param timestamp: is the time when the news from a module is send to be published in the outputfile
        :param news: contains news from modules (=channels)
        :param channels: are actually the keys to identify a module
        """
        row = {}
        row['time'] = timestamp.strftime('%H%M%S%f')

        row.update(self.filter_row(news=news, channels=channels))
        self.update_plot_data(row)

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
