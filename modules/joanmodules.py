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
    CONTROLLER_PLOTTER = auto()
    EXPERIMENT_MANAGER = auto()

    @property
    def manager(self):
        from modules.hardwaremanager.hardwaremanager_manager import HardwareManager
        from modules.template.template_manager import TemplateManager
        from modules.carlainterface.carlainterface_manager import CarlaInterfaceManager
        from modules.hapticcontrollermanager.hapticcontrollermanager_manager import HapticControllerManager
        from modules.controllerplotter.controllerplotter_manager import ControllerPlotterManager
        from modules.datarecorder.datarecorder_manager import DataRecorderManager
        from modules.experimentmanager.experimentmanager_manager import ExperimentManager

        return {JOANModules.HARDWARE_MANAGER: HardwareManager,
                JOANModules.TEMPLATE: TemplateManager,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceManager,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManager,
                JOANModules.CONTROLLER_PLOTTER: ControllerPlotterManager,
                JOANModules.DATA_RECORDER: DataRecorderManager,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManager}[self]

    @property
    def dialog(self):
        from modules.hardwaremanager.hardwaremanager_dialog import HardwareManagerDialog
        from modules.template.template_dialog import TemplateDialog
        from modules.carlainterface.carlainterface_dialog import CarlaInterfaceDialog
        from modules.hapticcontrollermanager.hapticcontrollermanager_dialog import HapticControllerManagerDialog
        from modules.controllerplotter.controllerplotter_dialog import ControllerPlotterDialog
        from modules.datarecorder.datarecorder_dialog import DataRecorderDialog
        from modules.experimentmanager.experimentmanager_dialog import ExperimentManagerDialog

        return {JOANModules.HARDWARE_MANAGER: HardwareManagerDialog,
                JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceDialog,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerDialog,
                JOANModules.DATA_RECORDER: DataRecorderDialog,
                JOANModules.CONTROLLER_PLOTTER: ControllerPlotterDialog,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerDialog}[self]

    @property
    def settings(self):
        from modules.template.template_settings import TemplateSettings
        from modules.hardwaremanager.hardwaremanager_settings import HardwareManagerSettings
        from modules.carlainterface.carlainterface_settings import CarlaInterfaceSettings
        from modules.hapticcontrollermanager.hapticcontrollermanager_settings import HapticControllerManagerSettings
        from modules.controllerplotter.controllerplotter_settings import ControllerPlotterSettings
        from modules.datarecorder.datarecorder_settings import DataRecorderSettings
        from modules.experimentmanager.experimentmanager_settings import ExperimentManagerSettings

        return {JOANModules.TEMPLATE: TemplateSettings,
                JOANModules.HARDWARE_MANAGER: HardwareManagerSettings,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceSettings,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerSettings,
                JOANModules.DATA_RECORDER: DataRecorderSettings,
                JOANModules.CONTROLLER_PLOTTER: ControllerPlotterSettings,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerSettings
                }[self]

    @property
    def shared_variables(self):
        from modules.hardwaremanager.hardwaremanager_sharedvariables import HardwareManagerSharedVariables
        from modules.template.template_sharedvalues import TemplateSharedVariables
        from modules.carlainterface.carlainterface_sharedvariables import CarlaInterfaceSharedVariables
        from modules.hapticcontrollermanager.hapticcontrollermanager_sharedvariables import HapticControllerManagerSharedVariables
        from core.modulesharedvariables import ModuleSharedVariables
        from modules.datarecorder.datarecorder_sharedvariables import DataRecorderSharedVariables

        return {JOANModules.HARDWARE_MANAGER: HardwareManagerSharedVariables,
                JOANModules.TEMPLATE: TemplateSharedVariables,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceSharedVariables,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerSharedVariables,
                JOANModules.CONTROLLER_PLOTTER: ModuleSharedVariables,
                JOANModules.DATA_RECORDER: DataRecorderSharedVariables,
                JOANModules.EXPERIMENT_MANAGER: ModuleSharedVariables}[self]

    @property
    def process(self):
        from modules.hardwaremanager.hardwaremanager_process import HardwareManagerProcess
        from modules.template.template_process import TemplateProcess
        from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
        from modules.hapticcontrollermanager.hapticcontrollermanager_process import HapticControllerManagerProcess
        from core.module_process import ModuleProcess
        from modules.datarecorder.datarecorder_process import DataRecorderProcess

        return {JOANModules.HARDWARE_MANAGER: HardwareManagerProcess,
                JOANModules.TEMPLATE: TemplateProcess,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceProcess,
                JOANModules.HAPTIC_CONTROLLER_MANAGER: HapticControllerManagerProcess,
                JOANModules.CONTROLLER_PLOTTER: ModuleProcess,
                JOANModules.DATA_RECORDER: DataRecorderProcess,
                JOANModules.EXPERIMENT_MANAGER: ModuleProcess}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/hardwaremanager_dialog.ui"),
                JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/template_dialog.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/carlainterface_dialog.ui"),
                JOANModules.HAPTIC_CONTROLLER_MANAGER: os.path.join(path_to_modules, "hapticcontrollermanager/hapticcontrollermanager_dialog.ui"),
                JOANModules.CONTROLLER_PLOTTER: os.path.join(path_to_modules, "controllerplotter/controllerplotter_dialog.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/datarecorder_dialog.ui"),
                JOANModules.EXPERIMENT_MANAGER: os.path.join(path_to_modules, "experimentmanager/experimentmanager.ui")
                }[self]

    def __str__(self):
        return {JOANModules.HARDWARE_MANAGER: 'Hardware Manager',
                JOANModules.TEMPLATE: 'Template',
                JOANModules.CARLA_INTERFACE: 'Carla Interface',
                JOANModules.HAPTIC_CONTROLLER_MANAGER: 'Haptic Controller Manager',
                JOANModules.CONTROLLER_PLOTTER: 'Controller Plotter',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                JOANModules.EXPERIMENT_MANAGER: 'Experiment Manager'}[self]

    @staticmethod
    def from_string_representation(string):
        for module in JOANModules:
            if str(module) == string:
                return module
        return None
