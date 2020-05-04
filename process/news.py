from modules.joanmodules import JOANModules


class News:
    """
    The News class is a singleton that holds all most recent news data
    Every class has its own writing area; the key of the class
    All other classes may read the value
    """
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(News)
            cls._news = {}

        return cls.instance

    def write_news(self, module: JOANModules, news_dict):
        self._news.update({module: news_dict})

    def read_news(self, module: JOANModules):
        try:
            return self._news[module]
        except KeyError:
            return {}

    @property
    def all_news(self):
        return self._news

    @property
    def all_news_keys(self):
        return self._news.keys()
