import copy

from core.module_settings import ModuleSettings
from core.news import News
from modules.joanmodules import JOANModules


class DataRecorderSettings(ModuleSettings):
    def __init__(self, module_enum: JOANModules):
        """
        Writes datarecorder settings which consist of news-variables to be written by the datarecorder
        and the write interval used by the datarecorder
        """
        super().__init__(module_enum)

        self.variables_to_save = {}
        self.existing_variables_to_save = {}
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

    def _set_new_entries_checked(self, element, variables_element):
        """
        Set only the new news-item in the variables_to_save to True 
        Existing news-items will get the existing value
        """
        if isinstance(element, dict):
            for key, value in element.items():
                if isinstance(value, dict):
                    try:
                        self._set_new_entries_checked(element.get(key), variables_element.get(key))
                    except (KeyError, TypeError) as e:
                        print(e)
                else:
                    try:
                        element[key] = variables_element[key]
                    except (KeyError, TypeError):
                        element[key] = True

    def refresh(self, existing_variables_to_save):
        """
        Every news item of every module(=channel) is taken to make a treelist of variables to save
        It also deletes the vehicle_object from the news if they are present.
        """
        news = News()
        for module in news.all_news_keys:
            self.existing_variables_to_save = copy.deepcopy(existing_variables_to_save)

            original_news = news.read_news(module)

            self._remove_forbidden_vartypes(original_news)

            module_news = copy.deepcopy(original_news)

            self.variables_to_save[str(module)] = module_news

        self._set_new_entries_checked(self.variables_to_save, self.existing_variables_to_save)

    def _remove_forbidden_vartypes(self, news_dict):
        """Loop through the news dict, check each entry (recursively) if they are not one of the allowed variable types, and delete them."""
        keys = list(news_dict.keys())

        for key in keys:
            value = news_dict.get(key)
            if not isinstance(value, (int, float, dict, bool, str)):
                try:
                    news_dict.pop(key)
                except KeyError:
                    pass
            elif isinstance(value, dict):
                # recursion
                self._remove_forbidden_vartypes(value)
            else:
                pass  # do nothing

    def get_variables_to_save(self):
        return self.variables_to_save
