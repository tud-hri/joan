from modules.joanmodules import JOANModules
from process.joanmodulesettings import JoanModuleSettings

from process.news import News
import copy

class DataPlotterSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        """
        Writes dataplotter settings which consist of news-variables and item-properties 
        to be written by the dataplotter and the write interval used by the dataplotter
        """
        super().__init__(module_enum)

        self.variables_to_save = {}
        self.write_interval = 100

        self.picklist_plot_windows = ["No", "plot 1", "plot 2", "plot 3", "plot 4"]
        self.picklist_line_types = ["solid", "dashed", "dotted"]
        self.picklist_line_colors = ["blue", "#000000"]

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
                    element_property["plot_window"] = self.picklist_plot_windows[0]
                    element_property["line_type"] = self.picklist_line_types[0]
                    element_property["line_color"] = self.picklist_line_colors[0]
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

    def get_variables_to_save(self):
        return self.variables_to_save

    def get_picklists(self):
        """
        return: a dictionary of picklists
        """
        return {'plot_windows': self.picklist_plot_windows,
                'line_types': self.picklist_line_types,
                'line_colors': self.picklist_line_colors}



