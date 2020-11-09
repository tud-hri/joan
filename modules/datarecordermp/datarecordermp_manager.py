from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from core.news import News


class DatarecorderMPManager(ModuleManager):
    """ Manages the datarecordermp environment """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.DATA_RECORDER, time_step_in_ms=time_step_in_ms, parent=parent)

    def initialize(self):
        print("init")
        news = News()
        readable_news = {}
        for _, member in JOANModules.__members__.items():
            readable_news.update({member: news.read_news(member)})
        #self._as_dict_for_dialog(self.readable_news)
        print(readable_news)

        return super().initialize()

    def get_ready(self):
        print("get ready")
        # create tree widget
        super().get_ready()
        self.module_dialog.create_tree_widget(self.singleton_news)

    def start(self):
        print("start")
        return super().start()

    def stop(self):
        print("stop")
        return super().stop()