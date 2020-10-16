import enum
from pathlib import Path
from datetime import datetime

from modules.joanmodules import JOANModules
from core.joanmodulesettings import JoanModuleSettings
from core.module_manager import ModuleManager

class TemplateMPSettings(JoanModuleSettings):
    def __init__(self, settings_filename='./default_settings.json'):
        super().__init__(JOANModules.TEMPLATE_MP)

        self.time_step = 100
        
        self.int_setting = 1
        self.float_setting = 1.5
        self.string_setting = 'Hello World'
        self.overwrite_when_instantiated = 'to be overwritten'
        self.enum_setting = CustomEnumSetting.BLUE
        self.custom_class_setting = CustomClassSetting()

        if Path(settings_filename).is_file():
            self.load_from_file(settings_filename)
            now = datetime.now()
            self.overwrite_when_instantiated = now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.time_step = 100  # set default if self.time_step does not exist
            self.save_to_file(settings_filename)


class CustomClassSetting:
    def __init__(self):
        self.nested_int_setting = 4
        self.nested_float_setting = 5.7
        self.nested_string_setting = 'Hello Again'


class CustomEnumSetting(enum.Enum):
    RED = 0xFF0000
    GREEN = 0x00FF00
    BLUE = 0x0000FF
