from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
#rom modules.datarecordermp.writermp.newswritermp import DataWriter
from datetime import datetime
import inspect
from core import News
from copy import deepcopy


class DatarecorderMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events)
        # it is possible to read from other modules
        # do NOT WRITE to other modules' news to prevent spaghetti-code
        self.shared_variables_hardware = news.read_news(JOANModules.HARDWARE_MP)
        self.shared_variables_template = news.read_news(JOANModules.TEMPLATE_MP)
        self._module_shared_variables = news.read_news(module)

        # somehow self.news = news ends up as an empty dict in the 
        # methods: get_ready do_while_running

        # so put the news in another variable, specific for reading
        self.readable_news = {}
        for _, member in JOANModules.__members__.items():
           self.readable_news.update({member: news.read_news(member)})
 
    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings are converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        print("\n\n\n")

        # show current shared values for this module
        #print(self._module_shared_variables.__dict__)

        # TODO: get data from all shared_variables (=news)
        #news_writer_mp = DataWriter()

    def do_while_running(self):
        """
        do_while_running something and, dfor datarecorder, read the result from a shared_variable
        """
        pass

        try:
            for _, member in JOANModules.__members__.items():
                shared_variables = self.readable_news.get(member)
                for variable in inspect.getmembers(shared_variables):
                    print(variable)
                    if not variable[0].startswith('_')  and type(variable[1]) in (int, str, float):
                        print(variable[0], variable[1])
        except Exception as inst:
            print('werkt niet omdat:, ', inst)

