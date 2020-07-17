from modules.joanmodules import JOANModules
from process.joanmodulesettings import JoanModuleSettings

from process.news import News
import copy

class DataRecorderSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        """
        Writes datarecorder settings which consist of news-variables to be written by the datarecorder
        and the write interval used by the datarecorder
        """
        super().__init__(module_enum)

        self.variables_to_save = {}
        self.write_interval = 100

    def _set_checked(self, element):
        """
        Set the news-item in the variables_to_save to True 
        """
        if isinstance(element, dict):
            for key, value in element.items():
                if isinstance(value, dict):
                    self._set_checked(element.get(key))
                else:
                    element[key] = True

    def set_all_true(self):
        """
        Every news item of every module(=channel) is taken to make a treelist of variables to save
        """
        news = News()
        for module in JOANModules:
            module_news = copy.deepcopy(news.read_news(module))
            self.variables_to_save[str(module)] = module_news
        self._set_checked(self.variables_to_save)

    def get_variables_to_save(self):
        return self.variables_to_save



