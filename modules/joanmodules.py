import enum
import os


class JOANModules(enum.Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, 
    just increment the ID number and make sure to add links to the action and dialog/widget
    classes.
    """

    TEMPLATE = -1
    DATA_RECORDER = 0
    HARDWARE_MANAGER = 1
    CARLA_INTERFACE = 2
    #EXPERIMENT_MANAGER = 3
    #STEERING_WHEEL_CONTROL = 4

    @property
    def action(self):
        from modules.template.action.templateaction import TemplateAction
        from modules.datarecorder.action.datarecorderaction import DatarecorderAction
        #from modules.steeringwheelcontrol.action.steeringwheelcontrolaction import SteeringWheelControlAction
        from modules.hardwaremanager.action.hardwaremanageraction import HardwaremanagerAction
        from modules.carlainterface.action.carlainterfaceaction import CarlainterfaceAction
        #from modules.experimentmanager.action.experimentmanageraction import ExperimentManagerAction
    
        return {JOANModules.TEMPLATE: TemplateAction,
                JOANModules.DATA_RECORDER: DatarecorderAction,
                #JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlAction,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerAction,
                JOANModules.CARLA_INTERFACE: CarlainterfaceAction
                #JOANModules.EXPERIMENT_MANAGER: ExperimentManagerAction
                }[self]

    @property
    def dialog(self):
        from modules.template.dialog.templatedialog import TemplateDialog
        from modules.datarecorder.dialog.datarecorderdialog import DatarecorderDialog
        #from modules.steeringwheelcontrol.dialog.steeringwheelcontroldialog import SteeringWheelControlDialog
        from modules.hardwaremanager.dialog.hardwaremanagerdialog import HardwaremanagerDialog
        from modules.carlainterface.dialog.carlainterfacedialog import CarlainterfaceDialog
        #from modules.experimentmanager.dialog.experimentmanagerdialog import ExperimentManagerDialog
        
        return {JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.DATA_RECORDER: DatarecorderDialog,
                #JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlDialog,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerDialog,
                JOANModules.CARLA_INTERFACE: CarlainterfaceDialog
                #JOANModules.EXPERIMENT_MANAGER: ExperimentManagerDialog
                }[self]

    @property
    def states(self):
        from modules.datarecorder.action.states import DatarecorderStates
        #from modules.experimentmanager.action.states import ExperimentManagerStates
        #from modules.steeringwheelcontrol.action.states import SteeringWheelControlStates
        
        return {JOANModules.DATA_RECORDER: DatarecorderStates
                #JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlStates,
                #JOANModules.EXPERIMENT_MANAGER: ExperimentManagerStates
                }[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/dialog/templatewidget.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/dialog/datarecorder.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/dialog/carlainterface.ui"),
                #JOANModules.STEERING_WHEEL_CONTROL: os.path.join(path_to_modules, "steeringwheelcontrol/dialog/steeringwheelcontrol.ui"),
                JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/dialog/hardwaremanager.ui")
                #JOANModules.EXPERIMENT_MANAGER: os.path.join(path_to_modules, "experimentmanager/dialog/experimentmanager.ui")
                }[self]

    def __str__(self):
        return {JOANModules.TEMPLATE: 'Template',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                #JOANModules.STEERING_WHEEL_CONTROL: 'Steering Wheel Control',
                JOANModules.HARDWARE_MANAGER: 'Hardware Communication',
                JOANModules.CARLA_INTERFACE: 'Carla Interface'
                #JOANModules.EXPERIMENT_MANAGER: 'Experiment Manager'
                }[self]
