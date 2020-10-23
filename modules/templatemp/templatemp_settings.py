import enum

from core.module_settings import ModuleSettings
from modules.joanmodules import JOANModules


class TemplateMPSettings(ModuleSettings):
    def __init__(self):
        super().__init__(JOANModules.TEMPLATE_MP)

        self.time_step = 100
        self.int_setting = 1
        self.float_setting = 1.5
        self.string_setting = 'Hello World'
        self.overwrite_with_current_time = 'current time'
        self.enum_setting = CustomEnumSetting.BLUE

        # settings can also be nested with 'sub' setting objects
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
