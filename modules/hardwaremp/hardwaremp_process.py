from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step, news):
        super().__init__(module, time_step=time_step, news=news)
        self.news = news.read_news(JOANModules.HARDWARE_MP)
        self.bleh = news.read_news('joe')
        print(self.bleh)
        print(self.news)


        self.keyboard = self.bleh['Keyboard 1']
        print(self.keyboard)







    def do_function(self):
        self.keyboard.do()
        pass

