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
    STEERING_WHEEL_CONTROL = 3
    TRAJECTORY_RECORDER = 4

    @property
    def action(self):
        from modules.template.action.templateaction import TemplateAction
        from modules.datarecorder.action.datarecorderaction import DatarecorderAction
        from modules.steeringwheelcontrol.action.steeringwheelcontrolaction import SteeringWheelControlAction
        from modules.hardwaremanager.action.hardwaremanageraction import HardwaremanagerAction
        from modules.carlainterface.action.carlainterfaceaction import CarlainterfaceAction
        from modules.trajectoryrecorder.action.trajectoryrecorder import TrajectoryrecorderAction

        return {JOANModules.TEMPLATE: TemplateAction,
                JOANModules.DATA_RECORDER: DatarecorderAction,
                JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlAction,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderAction,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerAction,
                JOANModules.CARLA_INTERFACE: CarlainterfaceAction}[self]

    @property
    def dialog(self):
        from modules.template.dialog.templatedialog import TemplateDialog
        from modules.datarecorder.dialog.datarecorderdialog import DatarecorderDialog
        from modules.steeringwheelcontrol.dialog.steeringwheelcontroldialog import SteeringWheelControlDialog
        from modules.trajectoryrecorder.widget.trajectoryrecorder import TrajectoryrecorderWidget
        from modules.hardwaremanager.dialog.hardwaremanagerdialog import HardwaremanagerDialog
        from modules.carlainterface.dialog.carlainterfacedialog import CarlainterfaceDialog
        
        return {JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.DATA_RECORDER: DatarecorderDialog,
                JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlDialog,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderWidget,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerDialog,
                JOANModules.CARLA_INTERFACE: CarlainterfaceDialog}[self]

    @property
    def states(self):
        from modules.template.action.states import TemplateStates
        from modules.datarecorder.action.states import DatarecorderStates
        from modules.steeringwheelcontrol.action.states import SteeringWheelControlStates
        from modules.trajectoryrecorder.action.states import TrajectoryrecorderStates
        from modules.hardwaremanager.action.states import HardwaremanagerStates
        from modules.carlainterface.action.states import CarlainterfaceStates
        
        return {JOANModules.TEMPLATE: TemplateStates,
                JOANModules.DATA_RECORDER: DatarecorderStates,
                JOANModules.STEERING_WHEEL_CONTROL: SteeringWheelControlStates,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderStates,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerStates,
                JOANModules.CARLA_INTERFACE: CarlainterfaceStates}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/dialog/templatewidget.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/dialog/carlainterface.ui"),
                JOANModules.TRAJECTORY_RECORDER: os.path.join(path_to_modules, "trajectoryrecorder/widget/trajectoryrecorder.ui"),
                JOANModules.STEERING_WHEEL_CONTROL: os.path.join(path_to_modules, "steeringwheelcontrol/dialog/steeringwheelcontrol.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/dialog/datarecorder.ui"),
                JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/dialog/hardwaremanager_ui.ui")}[self]

    def __str__(self):
        return {JOANModules.TEMPLATE: 'Template',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                JOANModules.STEERING_WHEEL_CONTROL: 'Steering Wheel Control',
                JOANModules.TRAJECTORY_RECORDER: 'Trajectory Recorder',
                JOANModules.HARDWARE_MANAGER: 'Hardware Communication',
                JOANModules.CARLA_INTERFACE: 'Carla Interface'}[self]
