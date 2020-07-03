from modules.joanmodules import JOANModules
from process.joanmodulesettings import JoanModuleSettings

from process.news import News
import copy

class DataRecorderSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        """
        settings for writing items are set checked by default,
        original news should not change, therefore using a deepcopy of the news
        """
        super().__init__(module_enum)

        news = News()
        self.variables_to_save = {}

        for module in JOANModules:
            module_news = copy.deepcopy(news.read_news(module))
            self.variables_to_save[str(module)] = module_news

        self._set_checked(self.variables_to_save)

    def _set_checked(self, element):
        if isinstance(element, dict):
            for key, value in element.items():
                if isinstance(value, dict):
                    self._set_checked(element.get(key))
                else:
                    element[key] = True


