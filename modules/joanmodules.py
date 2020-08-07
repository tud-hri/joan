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
    AGENT_MANAGER = 2
    STEERING_WHEEL_CONTROL = 3

    EXPERIMENT_MANAGER = 4

    @property
    def action(self):
        from modules.template.action.templateaction import TemplateAction
        from modules.datarecorder.action.datarecorderaction import DatarecorderAction
        from modules.steeringwheelcontrol.action.steeringwheelcontrolaction import SteeringWheelControlAction
        from modules.hardwaremanager.action.hardwaremanageraction import HardwaremanagerAction
        from modules.agentmanager.action.agentmanageraction import AgentmanagerAction
        from modules.experimentmanager.action.experimentmanageraction import ExperimentManagerAction
    
        return {JOANModules.TEMPLATE: TemplateAction,
                JOANModules.DATA_RECORDER: DatarecorderAction,
                JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlAction,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerAction,
                JOANModules.AGENT_MANAGER: AgentmanagerAction,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerAction,
                }[self]

    @property
    def dialog(self):
        from modules.template.dialog.templatedialog import TemplateDialog
        from modules.datarecorder.dialog.datarecorderdialog import DatarecorderDialog
        from modules.steeringwheelcontrol.dialog.steeringwheelcontroldialog import SteeringWheelControlDialog
        from modules.hardwaremanager.dialog.hardwaremanagerdialog import HardwaremanagerDialog
        from modules.agentmanager.dialog.agentmanagerdialog import AgentmanagerDialog
        from modules.experimentmanager.dialog.experimentmanagerdialog import ExperimentManagerDialog
        
        return {JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.DATA_RECORDER: DatarecorderDialog,
                JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlDialog,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerDialog,
                JOANModules.AGENT_MANAGER: AgentmanagerDialog,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerDialog,
                }[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/dialog/templatewidget.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/dialog/datarecorder.ui"),
                JOANModules.AGENT_MANAGER: os.path.join(path_to_modules, "agentmanager/dialog/agentmanager.ui"),
                JOANModules.STEERING_WHEEL_CONTROL: os.path.join(path_to_modules, "steeringwheelcontrol/dialog/steeringwheelcontrol.ui"),
                JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/dialog/hardwaremanager.ui"),
                JOANModules.EXPERIMENT_MANAGER: os.path.join(path_to_modules, "experimentmanager/dialog/experimentmanager_widget.ui"),
                }[self]

    def __str__(self):
        return {JOANModules.TEMPLATE: 'Template',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                JOANModules.STEERING_WHEEL_CONTROL: 'Steering Wheel Controller Manager',
                JOANModules.HARDWARE_MANAGER: 'Hardware Manager',
                JOANModules.AGENT_MANAGER: 'Agent Manager',
                JOANModules.EXPERIMENT_MANAGER: 'Experiment Manager',
                }[self]

    @staticmethod
    def from_string_representation(string):
        for module in JOANModules:
            if str(module) == string:
                return module
        return None
