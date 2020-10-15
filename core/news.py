from modules.joanmodules import JOANModules


class News:
    """
    The News class is a singleton that holds all most recent news data
    Every class has its own writing area; the key of the class
    All other classes may read the value
    """
    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = object.__new__(News)
            cls._news = {}

        return cls.instance

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
        try:
            del self._news[module]
        except KeyError as e:
            print(e)

    @property
    def all_news(self):
        return self._news

    @property
    def all_news_keys(self):
        return self._news.keys()
