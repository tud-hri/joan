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
    EXPERIMENT_MANAGER = 3
    FEED_BACK_CONTROLLER = 4
    TRAJECTORY_RECORDER = 5
    

    @property
    def action(self):
        from modules.template.action.templateaction import TemplateAction
        from modules.datarecorder.action.datarecorderaction import DatarecorderAction
        from modules.hardwaremanager.action.hardwaremanageraction import HardwaremanagerAction
        from modules.carlainterface.action.carlainterfaceaction import CarlainterfaceAction
        from modules.experimentmanager.action.experimentmanageraction import ExperimentManagerAction
        from modules.trajectoryrecorder.action.trajectoryrecorder import TrajectoryrecorderAction
        from modules.feedbackcontroller.action.feedbackcontroller import FeedbackcontrollerAction
        
        return {JOANModules.TEMPLATE: TemplateAction,
                JOANModules.DATA_RECORDER: DatarecorderAction,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerAction,
                JOANModules.CARLA_INTERFACE: CarlainterfaceAction,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerAction,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderAction,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerAction}[self]

    @property
    def dialog(self):
        from modules.template.dialog.templatedialog import TemplateDialog
        from modules.datarecorder.dialog.datarecorderdialog import DatarecorderDialog
        from modules.hardwaremanager.dialog.hardwaremanagerdialog import HardwaremanagerDialog
        from modules.carlainterface.dialog.carlainterfacedialog import CarlainterfaceDialog
        from modules.experimentmanager.dialog.experimentmanagerdialog import ExperimentManagerDialog
        from modules.trajectoryrecorder.widget.trajectoryrecorder import TrajectoryrecorderWidget
        from modules.feedbackcontroller.widget.feedbackcontroller import FeedbackcontrollerWidget
        
        return {JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.DATA_RECORDER: DatarecorderDialog,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerDialog,
                JOANModules.CARLA_INTERFACE: CarlainterfaceDialog,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerDialog,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderWidget,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerWidget}[self]

    @property
    def states(self):
        from modules.template.action.states import TemplateStates
        from modules.datarecorder.action.states import DatarecorderStates
        from modules.hardwaremanager.action.states import HardwaremanagerStates
        from modules.carlainterface.action.states import CarlainterfaceStates
        from modules.experimentmanager.action.states import ExperimentManagerStates
        from modules.trajectoryrecorder.action.states import TrajectoryrecorderStates
        from modules.feedbackcontroller.action.states import FeedbackcontrollerStates
        
        return {JOANModules.TEMPLATE: TemplateStates,
                JOANModules.DATA_RECORDER: DatarecorderStates,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerStates,
                JOANModules.CARLA_INTERFACE: CarlainterfaceStates,
                JOANModules.EXPERIMENT_MANAGER: ExperimentManagerStates,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderStates,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerStates}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/dialog/templatewidget.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/dialog/datarecorder.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/dialog/carlainterface.ui"),
                JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/dialog/hardwaremanager.ui"),
                JOANModules.EXPERIMENT_MANAGER: os.path.join(path_to_modules, "experimentmanager/dialog/experimentmanager.ui"),
                JOANModules.TRAJECTORY_RECORDER: os.path.join(path_to_modules, "trajectoryrecorder/widget/trajectoryrecorder.ui"),
                JOANModules.FEED_BACK_CONTROLLER: os.path.join(path_to_modules, "feedbackcontroller/widget/feedbackcontroller.ui")}[self]

    def __str__(self):
        return {JOANModules.TEMPLATE: 'Template',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                JOANModules.HARDWARE_MANAGER: 'Hardware Communication',
                JOANModules.CARLA_INTERFACE: 'Carla Interface',
                JOANModules.EXPERIMENT_MANAGER: 'Experiment Manager',
                JOANModules.TRAJECTORY_RECORDER: 'Trajectory Recorder',
                JOANModules.FEED_BACK_CONTROLLER: 'Feed Back Controller'}[self]
