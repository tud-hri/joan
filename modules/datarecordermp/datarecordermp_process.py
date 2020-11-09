from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules
#rom modules.datarecordermp.writermp.newswritermp import DataWriter
from datetime import datetime
import inspect
from core import News
from copy import deepcopy


class DatarecorderMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)

        # putting all modules which have settings (so which are being used) in a new readable_variables dict which we can use in our new process
        self.all_shared_variables = {}
        for key in settings_singleton.all_settings_keys:
            self.all_shared_variables[key] = news.read_news(key)
 
    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings are converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        print("\n\n\n")


        # show current shared values for this module

        # TODO: get data from all shared_variables, hier zitten alle geladen modules in:
        print(self.all_shared_variables)
        #news_writer_mp = DataWriter()

    def do_while_running(self):
        """
        do_while_running something and, dfor datarecorder, read the result from a shared_variable
        """
        #TODO kweenie precies wat hier de bedoeling was?


        # try:
        #     for _, member in JOANModules.__members__.items():
        #         all_shared_variables = self.readable_variables.get(member)
        #         for shared_variables in all_shared_variables.values():
        #             print(shared_variables)
        #         # print(shared_variables)
        #         # for variable in inspect.getmembers(shared_variables):
        #         #     if not variable[0].startswith('_')  and type(variable[1]) in (int, str, float):
        #         #         print(variable[0], variable[1])
        #         #         pass
        # except Exception as inst:
        #     print('werkt niet omdat:, ', inst)

