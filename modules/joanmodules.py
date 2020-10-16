import os
from enum import Enum, auto


class JOANModules(Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, 
    just increment the ID number and make sure to add links to the action and dialog/widget
    classes.
    """

    TEMPLATE_MP = auto()

    @property
    def manager(self):
        from modules.templatemp.templatemp_manager import TemplateMPManager

        return {JOANModules.TEMPLATE_MP: TemplateMPManager}[self]



    @property
    def dialog(self):
        from modules.templatemp.templatemp_dialog import TemplateMPDialog

        return {JOANModules.TEMPLATE_MP: TemplateMPDialog
                }[self]

    @property
    def sharedvalues(self):
        from modules.templatemp.templatemp_sharedvalues import TemplateMPSharedValues

        return {JOANModules.TEMPLATE_MP: TemplateMPSharedValues
                }[self]

    @property
    def process(self):
        from modules.templatemp.templatemp_process import TemplateMPProcess

        return {JOANModules.TEMPLATE_MP: TemplateMPProcess}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE_MP: os.path.join(path_to_modules, "templatemp/templatemp_widget.ui")
                }[self]

    def __str__(self):
        return {JOANModules.TEMPLATE_MP: 'Template MP'
                }[self]

    @staticmethod
    def from_string_representation(string):
        for module in JOANModules:
            if str(module) == string:
                return module
        return None
