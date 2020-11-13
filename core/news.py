from modules.joanmodules import JOANModules


class News:
    """
    The News class is a singleton that holds all the shared variables that contain the latest data
    """

    def __init__(self):
        self._news = {}

    def write_news(self, module: JOANModules, news_dict):
        """
        Write data to News for a module
        :param module: used as an identifier
        :param news_dict: dictionary (keys, values) with the new data
        """
        self._news.update({module: news_dict})

    def read_news(self, module: JOANModules):
        """
        Read new data from a module
        :param module:
        :return: requested data
        """
        try:
            return self._news[module]
        except KeyError:
            return {}

    def remove_news(self, module: JOANModules):
        """
        Remove module shared variable from News
        :param module: module enum
        :return:
        """
        try:
            del self._news[module]
        except KeyError as e:
            print('There is no news yet from',e)

    @property
    def all_news(self):
        return self._news

    @property
    def all_news_keys(self):
        return self._news.keys()
