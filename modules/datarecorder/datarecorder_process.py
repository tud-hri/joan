from core.module_process import ModuleProcess
from modules.datarecorder.datarecorder_settings import DatarecorderSettings
from modules.joanmodules import JOANModules


class DatarecorderProcess(ModuleProcess):
    settings: DatarecorderSettings

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)
        self.settings = settings
        self.news = news

        self.variables_to_be_saved = {}
        self.save_path = ''

        self.file = None

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings are converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        self.variables_to_be_saved = self.settings.variables_to_be_saved
        self.save_path = self.settings.path_to_save_file

        header = ', '.join(['.'.join(v) for v in self.variables_to_be_saved])
        with open(self.save_path, 'w') as self.file:
            self.file.write(header + '\n')

    def _run_loop(self):
        with open(self.save_path, 'a') as self.file:
            super()._run_loop()

    def do_while_running(self):
        """
        do_while_running something and, for datarecorder, read the result from a shared_variable
        """
        row = self._get_data_row()
        self.file.write(row + '\n')

    def _get_data_row(self):
        row = []
        for variable in self.variables_to_be_saved:
            module = JOANModules.from_string_representation(variable[0])
            last_object = self.news.read_news(module)

            for attribute_name in variable[1:]:
                if isinstance(last_object, dict):
                    last_object = last_object[attribute_name]
                elif isinstance(last_object, list):
                    last_object = last_object[int(attribute_name)]
                else:
                    last_object = getattr(last_object, attribute_name)

            row.append(str(last_object))

        return ', '.join(row)
