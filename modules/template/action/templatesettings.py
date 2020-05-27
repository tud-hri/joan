from process.joanmodulesettings import JoanModuleSettings
from modules.joanmodules import JOANModules


class TemplateSettings(JoanModuleSettings):
    def __init__(self):
        self.millis = 100

        self.int_setting = 1
        self.float_setting = 1.5
        self.string_setting = 'Hello World'
        self.enum_setting = JOANModules.TEMPLATE
        self.custom_class_setting = CustomClassSetting()


class CustomClassSetting:
    def __init__(self):
        self.nested_int_setting = 4
        self.nested_float_setting = 5.7
        self.nested_string_setting = 'Hello Again'
