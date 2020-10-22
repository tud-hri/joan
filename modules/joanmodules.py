import os
from enum import Enum, auto


class JOANModules(Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, 
    just increment the ID number and make sure to add links to the action and dialog/widget
    classes.
    """

    TEMPLATE_MP = auto()
    HARDWARE_MP = auto()

    @property
    def manager(self):
        from modules.hardwaremp.hardwaremp_manager import HardwareMPManager
        from modules.templatemp.templatemp_manager import TemplateMPManager

        return {JOANModules.HARDWARE_MP: HardwareMPManager,
                JOANModules.TEMPLATE_MP: TemplateMPManager}[self]

    @property
    def dialog(self):
        from modules.hardwaremp.hardwaremp_dialog import HardwareMPDialog
        from modules.templatemp.templatemp_dialog import TemplateMPDialog

        return {JOANModules.HARDWARE_MP: HardwareMPDialog,
                JOANModules.TEMPLATE_MP: TemplateMPDialog}[self]

    @property
    def settings(self):
        from modules.templatemp.templatemp_settings import TemplateMPSettings
        from modules.hardwaremp.hardwaremp_settings import HardwareMPSettings

        return {JOANModules.TEMPLATE_MP: TemplateMPSettings,
                JOANModules.HARDWARE_MP: HardwareMPSettings
                }[self]


    @property
    def shared_values(self):
        from modules.hardwaremp.hardwaremp_sharedvalues import HardwareMPSharedValues
        from modules.templatemp.templatemp_sharedvalues import TemplateMPSharedValues

        return {JOANModules.HARDWARE_MP: HardwareMPSharedValues,
                JOANModules.TEMPLATE_MP: TemplateMPSharedValues}[self]

    @property
    def process(self):
        from modules.hardwaremp.hardwaremp_process import HardwareMPProcess
        from modules.templatemp.templatemp_process import TemplateMPProcess

        return {JOANModules.HARDWARE_MP: HardwareMPProcess,
                JOANModules.TEMPLATE_MP: TemplateMPProcess}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.HARDWARE_MP: os.path.join(path_to_modules, "hardwaremp/hardwaremp_dialog.ui"),
                JOANModules.TEMPLATE_MP: os.path.join(path_to_modules, "templatemp/templatemp_dialog.ui")}[self]

    def __str__(self):
        return {JOANModules.HARDWARE_MP: 'Hardware MP',
                JOANModules.TEMPLATE_MP: 'Template MP'}[self]

    @staticmethod
    def from_string_representation(string):
        for module in JOANModules:
            if str(module) == string:
                return module
        return None
