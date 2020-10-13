import os
from enum import Enum, auto


class JOANModules(Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, 
    just increment the ID number and make sure to add links to the action and dialog/widget
    classes.
    """

    TEMPLATE = auto()
    DATA_RECORDER = auto()
    HARDWARE_MANAGER = auto()
    CARLA_INTERFACE = auto()
    STEERING_WHEEL_CONTROL = auto()
    EXPERIMENT_MANAGER = auto()
    DATA_PLOTTER = auto()
    SCENARIOS = auto()
    CONTROLLER_PLOTTER = auto()
    TEMPLATE_MP = auto()

    @property
    def manager(self):
        from modules.templatemp.templatempmanager import TemplateMPManager

        return {JOANModules.TEMPLATE_MP: TemplateMPManager}[self]

    @property
    def action(self):
        from modules.template.action.templateaction import TemplateAction
        from modules.datarecorder.action.datarecorderaction import DataRecorderAction
        from modules.steeringwheelcontrol.action.steeringwheelcontrolaction import SteeringWheelControlAction
        from modules.hardwaremanager.action.hardwaremanageraction import HardwareManagerAction
        from modules.dataplotter.action.dataplotteraction import DataplotterAction
        from modules.carlainterface.action.carlainterfaceaction import CarlaInterfaceAction
        from modules.experimentmanager.action.experimentmanageraction import ExperimentManagerAction
        from modules.scenarios.action.scenariosaction import ScenariosAction
        from modules.controllerplotter.action.controllerplotteraction import ControllerPlotterAction

        return {JOANModules.TEMPLATE: TemplateAction,
                JOANModules.DATA_RECORDER: DataRecorderAction,
                JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlAction,
                JOANModules.HARDWARE_MANAGER: HardwareManagerAction,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceAction,
                JOANModules.DATA_PLOTTER: DataplotterAction,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerAction,
                JOANModules.SCENARIOS: ScenariosAction,
                JOANModules.CONTROLLER_PLOTTER: ControllerPlotterAction
                }[self]

    @property
    def dialog(self):
        from modules.template.dialog.templatedialog import TemplateDialog
        from modules.datarecorder.dialog.datarecorderdialog import DataRecorderDialog
        from modules.steeringwheelcontrol.dialog.steeringwheelcontroldialog import SteeringWheelControlDialog
        from modules.hardwaremanager.dialog.hardwaremanagerdialog import HardwareManagerDialog
        from modules.dataplotter.dialog.dataplotterdialog import DataplotterDialog
        from modules.carlainterface.dialog.carlainterfacedialog import CarlaInterfaceDialog
        from modules.experimentmanager.dialog.experimentmanagerdialog import ExperimentManagerDialog
        from modules.scenarios.dialog.scenariosdialog import ScenariosDialog
        from modules.controllerplotter.dialog.controllerplotterdialog import ControllerPlotterDialog
        from modules.templatemp.templatempdialog import TemplateMPDialog

        return {JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.DATA_RECORDER: DataRecorderDialog,
                JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlDialog,
                JOANModules.HARDWARE_MANAGER: HardwareManagerDialog,
                JOANModules.CARLA_INTERFACE: CarlaInterfaceDialog,
                JOANModules.DATA_PLOTTER: DataplotterDialog,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerDialog,
                JOANModules.SCENARIOS: ScenariosDialog,
                JOANModules.CONTROLLER_PLOTTER: ControllerPlotterDialog,
                JOANModules.TEMPLATE_MP: TemplateMPDialog
                }[self]

    @property
    def sharedvalues(self):
        from modules.templatemp.templatempsharedvalues import TemplateMPSharedValues

        return {JOANModules.TEMPLATE_MP: TemplateMPSharedValues
                }[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/dialog/templatewidget.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/dialog/datarecorder.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/dialog/carlainterface.ui"),
                JOANModules.STEERING_WHEEL_CONTROL: os.path.join(path_to_modules,
                                                                 "steeringwheelcontrol/dialog/steeringwheelcontrol.ui"),
                JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/dialog/hardwaremanager.ui"),
                JOANModules.DATA_PLOTTER: os.path.join(path_to_modules, "dataplotter/dialog/dataplotter.ui"),
                JOANModules.EXPERIMENT_MANAGER: os.path.join(path_to_modules,
                                                             "experimentmanager/dialog/experimentmanager_widget.ui"),
                JOANModules.SCENARIOS: os.path.join(path_to_modules, "scenarios/dialog/scenarios.ui"),
                JOANModules.CONTROLLER_PLOTTER: os.path.join(path_to_modules, "controllerplotter/dialog/controllerplotter.ui"),
                JOANModules.TEMPLATE_MP: os.path.join(path_to_modules, "templatemp/templatempwidget.ui")
                }[self]

    def __str__(self):
        return {JOANModules.TEMPLATE: 'Template',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                JOANModules.STEERING_WHEEL_CONTROL: 'Steering Wheel Controller Manager',
                JOANModules.HARDWARE_MANAGER: 'Hardware Manager',
                JOANModules.EXPERIMENT_MANAGER: 'Experiment Manager',
                JOANModules.CARLA_INTERFACE: 'Carla Interface',
                JOANModules.DATA_PLOTTER: 'Data Plotter',
                JOANModules.SCENARIOS: 'Scenarios',
                JOANModules.CONTROLLER_PLOTTER: 'Controller Plotter',
                JOANModules.TEMPLATE_MP: 'Template MP'
                }[self]

    @staticmethod
    def from_string_representation(string):
        for module in JOANModules:
            if str(module) == string:
                return module
        return None
