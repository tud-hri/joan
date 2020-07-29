import os

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.settings import ModuleSettings


class ExperimentManagerAction(JoanModuleAction):
    def __init__(self, millis=100):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, millis=millis)

        self.data = {}
        self.write_news(news=self.data)

        # set factory settings per module, must be called before self.write_default_experiment()
        self._set_factory_settings_in_singleton()

        # create/get default experiment_settings
        self.my_file = os.path.join('.', 'default_experiment_settings.json')
        # First remove current file
        if os.path.exists(self.my_file):
            os.remove(self.my_file)
        self.settings_object = ModuleSettings(file=self.my_file)
        self.settings = self.settings_object.read_settings()
        self.settings.update(self._get_attention_message())
        self.share_settings(self.settings)

        self.write_default_experiment()  # maybe used as an example for experiment conditions
        self.experiment_settings = {}  # will contain experiment_settings
        self.condition_names = []  # will contain condition_names for use in getting correct settings

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        # self.write_news(news=self.data)
