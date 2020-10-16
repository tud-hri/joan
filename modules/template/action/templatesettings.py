import enum

from modules.joanmodules import JOANModules
from module_settings import ModuleSettings

class TemplateSettings(ModuleSettings):
    def __init__(self, module_enum: JOANModules):
        super().__init__(module_enum)
        self.millis = 100

        self.int_setting = 1
        self.float_setting = 1.5
        self.string_setting = 'Hello World'
        self.enum_setting = CustomEnumSetting.BLUE
        self.custom_class_setting = CustomClassSetting()


class CustomClassSetting:
    def __init__(self):
        self.nested_int_setting = 4
        self.nested_float_setting = 5.7
        self.nested_string_setting = 'Hello Again'


class CustomEnumSetting(enum.Enum):
    RED = 0xFF0000
    GREEN = 0x00FF00
    BLUE = 0x0000FF
