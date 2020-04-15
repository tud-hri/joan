import enum
import os


class JOANModules(enum.Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, just increment the ID number and make sure to add links to the action and widget
    classes.
    """

    TEMPLATE = -1
    DATA_RECORDER = 0
    FEED_BACK_CONTROLLER = 1
    HARDWARE_COMMUNICATION = 2
    CARLA_INTERFACE = 3
    TRAJECTORY_RECORDER = 4

    @property
    def action(self):
        from modules.template.action.templateaction import TemplateAction
        from modules.datarecorder.action.datarecorder import DatarecorderAction
        from modules.feedbackcontroller.action.feedbackcontroller import FeedbackcontrollerAction
        from modules.hardwarecommunication.action.hardwarecommunication import HardwarecommunicationAction
        from modules.siminterface.action.siminterface import SiminterfaceAction
        from modules.trajectoryrecorder.action.trajectoryrecorder import TrajectoryrecorderAction

        return {JOANModules.TEMPLATE: TemplateAction,
                JOANModules.DATA_RECORDER: DatarecorderAction,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerAction,
                JOANModules.HARDWARE_COMMUNICATION: HardwarecommunicationAction,
                JOANModules.CARLA_INTERFACE: SiminterfaceAction,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderAction}[self]

    @property
    def dialog(self):
        from modules.template.dialog.templatedialog import TemplateDialog
        from modules.datarecorder.widget.datarecorder import DatarecorderWidget
        from modules.feedbackcontroller.widget.feedbackcontroller import FeedbackcontrollerWidget
        from modules.hardwarecommunication.widget.hardwarecommunication import HardwarecommunicationWidget
        from modules.siminterface.widget.siminterface import SiminterfaceWidget
        from modules.trajectoryrecorder.widget.trajectoryrecorder import TrajectoryrecorderWidget

        return {JOANModules.TEMPLATE: TemplateDialog,
                JOANModules.DATA_RECORDER: DatarecorderWidget,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerWidget,
                JOANModules.HARDWARE_COMMUNICATION: HardwarecommunicationWidget,
                JOANModules.CARLA_INTERFACE: SiminterfaceWidget,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderWidget}[self]

    @property
    def states(self):
        from modules.template.action.states import TemplateStates
        from modules.datarecorder.action.states import DatarecorderStates
        from modules.feedbackcontroller.action.states import FeedbackcontrollerStates
        from modules.hardwarecommunication.action.states import HardwarecommunicationStates
        from modules.siminterface.action.states import SiminterfaceStates
        from modules.trajectoryrecorder.action.states import TrajectoryrecorderStates

        return {JOANModules.TEMPLATE: TemplateStates,
                JOANModules.DATA_RECORDER: DatarecorderStates,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerStates,
                JOANModules.HARDWARE_COMMUNICATION: HardwarecommunicationStates,
                JOANModules.CARLA_INTERFACE: SiminterfaceStates,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderStates}[self]

    @property
    def ui_file(self):
        path_to_modules = os.path.dirname(os.path.realpath(__file__))
        return {JOANModules.TEMPLATE: os.path.join(path_to_modules, "template/dialog/templatewidget.ui"),
                JOANModules.DATA_RECORDER: os.path.join(path_to_modules, "datarecorder/widget/datarecorder.ui"),
                JOANModules.FEED_BACK_CONTROLLER: os.path.join(path_to_modules, "feedbackcontroller/widget/feedbackcontroller.ui"),
                JOANModules.HARDWARE_COMMUNICATION: os.path.join(path_to_modules, "hardwarecommunication/widget/hardwarecommunication.ui"),
                JOANModules.CARLA_INTERFACE: os.path.join(path_to_modules, "siminterface/widget/siminterface.ui"),
                JOANModules.TRAJECTORY_RECORDER: os.path.join(path_to_modules, "trajectoryrecorder/widget/trajectoryrecorder.ui")}[self]

    def __str__(self):
        return {JOANModules.TEMPLATE: 'Template Module',
                JOANModules.DATA_RECORDER: 'Data Recorder',
                JOANModules.FEED_BACK_CONTROLLER: 'Feed Back Controller',
                JOANModules.HARDWARE_COMMUNICATION: 'Hardware Communication',
                JOANModules.CARLA_INTERFACE: 'Carla Interface',
                JOANModules.TRAJECTORY_RECORDER: 'Trajectory Recorder'}[self]
