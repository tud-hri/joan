import os
from enum import Enum, auto


class JOANModules(Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, 
    just increment the ID number and make sure to add links to the action and dialog/widget
    classes.
    """

    TEMPLATE = auto()
    HARDWARE_MANAGER = auto()
    CARLA_INTERFACE = auto()
    HAPTIC_CONTROLLER_MANAGER = auto()
    DATA_RECORDER = auto()

    @property
    def manager(self):
        from modules.hardwaremanager.hardwaremanager import HardwareManager
        from modules.template.template import TemplateManager
        from modules.carlainterface.carlainterface_manager import CarlaInterfaceManager
        from modules.hapticcontrollermanager.hapticcontrollermanager import HapticControllerManager
        from modules.datarecordermp.datarecordermp_manager import DatarecorderMPManager

        return {JOANModules.HARDWARE_MANAGER: HardwareManager,
                JOANModules.TEMPLATE: TemplateManager,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceManager,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManager,
                JOANModules.DATA_RECORDER: DatarecorderMPManager}[self]

    @property
    def dialog(self):
        from modules.hardwaremanager.hardwaremanager_dialog import HardwareManagerDialog
        from modules.template.template_dialog import TemplateDialog
        from modules.carlainterface.carlainterface_dialog import CarlaInterfaceDialog
        from modules.hapticcontrollermanager.hapticcontrollermanager_dialog import HapticControllerManagerDialog
        from modules.datarecordermp.datarecordermp_dialog import DatarecorderMPDialog

        return {JOANModules.HARDWARE_MANAGER: HardwareManagerDialog,
                JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceDialog,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerDialog,
                JOANModules.DATA_RECORDER: DatarecorderMPDialog}[self]

    @property
    def settings(self):
        from modules.template.template_settings import TemplateSettings
        from modules.hardwaremanager.hardwaremanager_settings import HardwareMPSettings
        from modules.carlainterface.carlainterface_settings import CarlaInterfaceSettings
        from modules.hapticcontrollermanager.hapticcontrollermanager_settings import HapticControllerManagerSettings
        from modules.datarecordermp.datarecordermp_settings import DatarecorderMPSettings

        return {JOANModules.TEMPLATE: TemplateSettings,
                JOANModules.HARDWARE_MANAGER: HardwareMPSettings,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceSettings,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerSettings,
                JOANModules.DATA_RECORDER: DatarecorderMPSettings
                }[self]

    @property
    def shared_variables(self):
        from modules.hardwaremanager.hardwaremanager_sharedvariables import HardwareSharedVariables
        from modules.template.template_sharedvalues import TemplateSharedVariables
        from modules.carlainterface.carlainterface_sharedvalues import CarlaInterfaceSharedVariables
        from modules.hapticcontrollermanager.hapticcontrollermanager_sharedvalues import HapticControllerManagerSharedVariables
        from modules.datarecordermp.datarecordermp_sharedvalues import DataRecorderMPSharedValues

        return {JOANModules.HARDWARE_MANAGER: HardwareSharedVariables,
                JOANModules.TEMPLATE: TemplateSharedVariables,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceSharedVariables,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerSharedVariables,
                JOANModules.DATA_RECORDER: DataRecorderMPSharedValues}[self]

    @property
    def process(self):
        from modules.hardwaremanager.hardwaremanager_process import HardwareManagerProcess
        from modules.template.template_process import TemplateProcess
        from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
        from modules.hapticcontrollermanager.hapticcontrollermanager_process import HapticControllerManagerProcess
        from modules.datarecordermp.datarecordermp_process import DatarecorderMPProcess

        return {JOANModules.HARDWARE_MANAGER: HardwareManagerProcess,
                JOANModules.TEMPLATE: TemplateProcess,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceProcess,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerProcess,
                JOANModules.DATA_RECORDER: DatarecorderMPProcess}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/hardwaremanager_dialog.ui"),
                JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/template_dialog.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/carlainterface_dialog.ui"),
                JOANModules.HAPTIC_CONTROLLER_MANAGER: os.path.join(path_to_modules, "hapticcontrollermanager/hapticcontrollermanager_dialog.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecordermp/datarecordermp_dialog.ui") }[self]

    def __str__(self):
        return {JOANModules.HARDWARE_MANAGER: 'Hardware Manager',
                JOANModules.TEMPLATE: 'Template',
                JOANModules.CARLA_INTERFACE: 'Carla Interface',
                JOANModules.HAPTIC_CONTROLLER_MANAGER:'Haptic Controller Manager',
                JOANModules.DATA_RECORDER: 'Data Recorder'}[self]

    @staticmethod
    def from_string_representation(string):
        for module in JOANModules:
            if str(module) == string:
                return module
        return None
