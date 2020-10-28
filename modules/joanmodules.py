import os
from enum import Enum, auto


class JOANModules(Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, 
    just increment the ID number and make sure to add links to the action and dialog/widget
    classes.
    """

    TEMPLATE = auto()
    HARDWARE_MP = auto()
    CARLA_INTERFACE = auto()

    @property
    def manager(self):
        from modules.hardwaremp.hardwaremp_manager import HardwareMPManager
        from modules.template.template_manager import TemplateManager
        from modules.carlainterface.carlainterface_manager import CarlaInterfaceManager

        return {JOANModules.HARDWARE_MP: HardwareMPManager,
                JOANModules.TEMPLATE: TemplateManager,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceManager}[self]

    @property
    def dialog(self):
        from modules.hardwaremp.hardwaremp_dialog import HardwareMPDialog
        from modules.template.template_dialog import TemplateDialog
        from modules.carlainterface.carlainterface_dialog import CarlaInterfaceDialog

        return {JOANModules.HARDWARE_MP: HardwareMPDialog,
                JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceDialog}[self]

    @property
    def settings(self):
        from modules.template.template_settings import TemplateSettings
        from modules.hardwaremp.hardwaremp_settings import HardwareMPSettings
        from modules.carlainterface.carlainterface_settings import CarlaInterfaceSettings

        return {JOANModules.TEMPLATE: TemplateSettings,
                JOANModules.HARDWARE_MP: HardwareMPSettings,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceSettings
                }[self]


    @property
    def shared_variables(self):
        from modules.hardwaremp.hardwaremp_sharedvariables import HardwareSharedVariables
        from modules.template.template_sharedvalues import TemplateSharedVariables
        from modules.carlainterface.carlainterface_sharedvalues import CarlaInterfaceSharedVariables

        return {JOANModules.HARDWARE_MP: HardwareSharedVariables,
                JOANModules.TEMPLATE: TemplateSharedVariables,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceSharedVariables}[self]

    @property
    def process(self):
        from modules.hardwaremp.hardwaremp_process import HardwareMPProcess
        from modules.template.template_process import TemplateProcess
        from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess

        return {JOANModules.HARDWARE_MP: HardwareMPProcess,
                JOANModules.TEMPLATE: TemplateProcess,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceProcess}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.HARDWARE_MP: os.path.join(path_to_modules, "hardwaremp/hardwaremp_dialog.ui"),
                JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/template_dialog.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/carlainterface_dialog.ui")}[self]

    def __str__(self):
        return {JOANModules.HARDWARE_MP: 'Hardware MP',
                JOANModules.TEMPLATE: 'Template',
                JOANModules.CARLA_INTERFACE: 'Carla Interface'}[self]

    @staticmethod
    def from_string_representation(string):
        for module in JOANModules:
            if str(module) == string:
                return module
        return None
