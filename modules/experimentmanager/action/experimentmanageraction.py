import os

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.settings import ModuleSettings


class ExperimentManagerAction(JoanModuleAction):
    def __init__(self, millis=100):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, millis=millis)

        self.data = {}
        self.write_news(news=self.data)

        # create/get default experiment_settings
        self.my_file = os.path.join('.', 'default_experiment_settings.json')
        # First remove current file
        if os.path.exists(self.my_file):
            os.remove(self.my_file)

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        # self.write_news(news=self.data)
