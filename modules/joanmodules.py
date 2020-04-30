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

    @property
    def action(self):
        from modules.template.action.templateaction import TemplateAction
        from modules.datarecorder.action.datarecorderaction import DatarecorderAction
        # from modules.feedbackcontroller.action.feedbackcontroller import FeedbackcontrollerAction
        from modules.hardwaremanager.action.hardwaremanageraction import HardwaremanagerAction
        from modules.carlainterface.action.carlainterfaceaction import CarlainterfaceAction
        # from modules.trajectoryrecorder.action.trajectoryrecorder import TrajectoryrecorderAction

        return {JOANModules.TEMPLATE: TemplateAction,
                JOANModules.DATA_RECORDER: DatarecorderAction,
                # JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerAction,
                # JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderAction,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerAction,
                JOANModules.CARLA_INTERFACE: CarlainterfaceAction}[self]

    @property
    def dialog(self):
        from modules.template.dialog.templatedialog import TemplateDialog
        from modules.datarecorder.dialog.datarecorderdialog import DatarecorderDialog
        # from modules.feedbackcontroller.widget.feedbackcontroller import FeedbackcontrollerWidget
        # from modules.trajectoryrecorder.widget.trajectoryrecorder import TrajectoryrecorderWidget
        from modules.hardwaremanager.dialog.hardwaremanagerdialog import HardwaremanagerDialog
        from modules.carlainterface.dialog.carlainterfacedialog import CarlainterfaceDialog
        
        return {JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.DATA_RECORDER: DatarecorderDialog,
                # JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerWidget,
                # JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderWidget,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerDialog,
                JOANModules.CARLA_INTERFACE: CarlainterfaceDialog}[self]

    @property
    def states(self):
        from modules.template.action.states import TemplateStates
        from modules.datarecorder.action.states import DatarecorderStates
        # from modules.feedbackcontroller.action.states import FeedbackcontrollerStates
        # from modules.trajectoryrecorder.action.states import TrajectoryrecorderStates
        from modules.hardwaremanager.action.states import HardwaremanagerStates
        from modules.carlainterface.action.states import CarlainterfaceStates
        
        return {JOANModules.TEMPLATE: TemplateStates,
                JOANModules.DATA_RECORDER: DatarecorderStates,
                # JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerStates,
                # JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderStates,
                JOANModules.HARDWARE_MANAGER: HardwaremanagerStates,
                JOANModules.CARLA_INTERFACE: CarlainterfaceStates}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/dialog/templatewidget.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "carlainterface/dialog/carlainterface.ui"),
                # JOANModules.TRAJECTORY_RECORDER: os.path.join(path_to_modules, "trajectoryrecorder/widget/trajectoryrecorder.ui"),
                # JOANModules.FEED_BACK_CONTROLLER: os.path.join(path_to_modules, "feedbackcontroller/widget/feedbackcontroller.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/dialog/datarecorder.ui"),
                JOANModules.HARDWARE_MANAGER: os.path.join(path_to_modules, "hardwaremanager/dialog/hardwaremanager_ui.ui")}[self]

    def __str__(self):
        return {JOANModules.TEMPLATE: 'Template',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                # JOANModules.FEED_BACK_CONTROLLER: 'Feed Back Controller',
                # JOANModules.TRAJECTORY_RECORDER: 'Trajectory Recorder',
                JOANModules.HARDWARE_MANAGER: 'Hardware Communication',
                JOANModules.CARLA_INTERFACE: 'Carla Interface'}[self]
