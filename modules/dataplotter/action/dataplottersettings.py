from modules.joanmodules import JOANModules
from process.joanmodulesettings import JoanModuleSettings

from process.news import News
import copy

from enum import Enum
from PyQt5 import QtCore

class PlotWindows(Enum):
    KEY = -1
    NOPLOT = 0
    PLOT1 = 1
    PLOT2 = 2
    PLOT3 = 3
    PLOT4 = 4

    def __str__(self):
        return {PlotWindows.KEY: 'plot_window',
                PlotWindows.NOPLOT: 'No',
                PlotWindows.PLOT1: 'Plot 1',
                PlotWindows.PLOT2: 'Plot 2',
                PlotWindows.PLOT3: 'Plot 3',
                PlotWindows.PLOT4: 'Plot 4'
                }[self]

    def reverse(self):
        return {str(PlotWindows.KEY): PlotWindows.KEY,
                str(PlotWindows.NOPLOT): PlotWindows.NOPLOT,
                str(PlotWindows.PLOT1): PlotWindows.PLOT1,
                str(PlotWindows.PLOT2): PlotWindows.PLOT2,
                str(PlotWindows.PLOT3): PlotWindows.PLOT3,
                str(PlotWindows.PLOT4): PlotWindows.PLOT4
                }[self]


class LineTypes(Enum):
    KEY = -1
    SOLID = 0
    DASHED = 1
    DOTTED = 2

    def view(self):
        return {LineTypes.SOLID: QtCore.Qt.SolidLine,
                LineTypes.DASHED: QtCore.Qt.DashLine,
                LineTypes.DOTTED: QtCore.Qt.DotLine
                }[self]

    def __str__(self):
        return {LineTypes.KEY: 'line_type',
                LineTypes.SOLID: 'solid',
                LineTypes.DASHED: 'dashed',
                LineTypes.DOTTED: 'dotted'
                }[self]

    def reverse(self):
        return {str(LineTypes.KEY): LineTypes.KEY,
                str(LineTypes.SOLID): LineTypes.SOLID,
                str(LineTypes.DASHED): LineTypes.DASHED,
                str(LineTypes.DOTTED): LineTypes.DOTTED
                }[self]

class LineColors(Enum):
    KEY = -1
    BLACK = 0
    BLUE = 1
    RED = 2
    GREEN = 3

    def color(self):
        return {LineColors.BLACK: '#000000',
                LineColors.BLUE: '#0000FF',
                LineColors.RED: '#FF0000',
                LineColors.GREEN: '#00FF00'
                }[self]

    def __str__(self):
        return {LineColors.KEY: 'line_color',
                LineColors.BLACK: 'zwart',
                LineColors.BLUE: 'blue',
                LineColors.RED: 'red',
                LineColors.GREEN: 'green'
                }[self]

    def reverse(self):
        return {str(LineColors.KEY): LineColors.KEY,
                str(LineColors.BLACK): LineColors.BLACK,
                str(LineColors.BLUE): LineColors.BLUE,
                str(LineColors.RED): LineColors.RED,
                str(LineColors.GREEN): LineColors.GREEN
                }[self]


class DataPlotterSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        """
        Writes dataplotter settings which consist of news-variables and item-properties 
        to be written by the dataplotter and the write interval used by the dataplotter
        """
        super().__init__(module_enum)

        self.variables_to_save = {}
        self.existing_variables_to_save = {}
        self.write_interval = 100

        self.picklist_plot_windows = [str(e) for e in PlotWindows]
        self.picklist_plot_windows.remove(str(PlotWindows.KEY))

        self.picklist_line_types = [str(e) for e in LineTypes]
        self.picklist_line_types.remove(str(LineTypes.KEY))

        self.picklist_line_colors = [str(e) for e in LineColors]
        self.picklist_line_colors.remove(str(LineColors.KEY))

    def _set_properties_empty(self, element):
        """
        Set the news-item in the variables_to_save to empty/default values
        """
        if isinstance(element, dict):
            for key, value in element.items():
                if isinstance(value, dict):
                    self._set_properties_empty(element.get(key))
                else:
                    element_property = {}
                    element_property[str(PlotWindows.KEY)] = str(PlotWindows.NOPLOT)
                    element_property[str(LineTypes.KEY)] = str(LineTypes.SOLID)
                    element_property[str(LineColors.KEY)] = str(LineColors.BLACK)
                    element[key] = element_property

    def set_all_empty(self):
        """
        Every news item of every module(=channel) is taken to make a treelist of variables to save
        """
        news = News()
        for module in JOANModules:
            module_news = copy.deepcopy(news.read_news(module))
            self.variables_to_save[str(module)] = module_news
        self._set_properties_empty(self.variables_to_save)


    def _set_new_entries_empty(self, element, variables_element):
        """
        Set only the new news-item in the variables_to_save to True 
        Existing news-items will get the existing value
        """
        if isinstance(element, dict):
            for key, value in element.items():
                if isinstance(value, dict):
                    self._set_new_entries_empty(element.get(key), variables_element.get(key))
                else:
                    try:
                        element[key] = variables_element[key]
                    except (KeyError, TypeError):
                        element_property = {}
                        element_property[str(PlotWindows.KEY)] = str(PlotWindows.NOPLOT)
                        element_property[str(LineTypes.KEY)] = str(LineTypes.SOLID)
                        element_property[str(LineColors.KEY)] = str(LineColors.BLACK)
                        element[key] = element_property

    def refresh(self, existing_variables_to_save):
        """
        Every news item of every module(=channel) is taken to make a treelist of variables to save
        """
        news = News()
        for module in JOANModules:
            self.existing_variables_to_save = copy.deepcopy(existing_variables_to_save)
            module_news = copy.deepcopy(news.read_news(module))
            self.variables_to_save[str(module)] = module_news
        self._set_new_entries_empty(self.variables_to_save, self.existing_variables_to_save)



    def get_variables_to_save(self):
        return self.variables_to_save




