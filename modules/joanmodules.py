import enum

from modules.datarecorder.action.datarecorder import DatarecorderAction
from modules.datarecorder.widget.datarecorder import DatarecorderWidget
from modules.feedbackcontroller.action.feedbackcontroller import FeedbackcontrollerAction
from modules.feedbackcontroller.widget.feedbackcontroller import FeedbackcontrollerWidget
from modules.hardwarecommunication.action.hardwarecommunication import HardwarecommunicationAction
from modules.hardwarecommunication.widget.hardwarecommunication import HardwarecommunicationWidget
from modules.siminterface.action.siminterface import SiminterfaceAction
from modules.siminterface.widget.siminterface import SiminterfaceWidget
from modules.trajectoryrecorder.action.trajectoryrecorder import TrajectoryrecorderAction
from modules.trajectoryrecorder.widget.trajectoryrecorder import TrajectoryrecorderWidget


class JOANModules(enum.Enum):
    """
    Enum to represent all available modules in JOAN. If you want to add a new module, just increment the ID number and make sure to add links to the action and widget
    classes.
    """

    DATA_RECORDER = 0
    FEED_BACK_CONTROLLER = 1
    HARDWARE_COMMUNICATION = 2
    CARLA_INTERFACE = 3
    TRAJECTORY_RECORDER = 4

    @property
    def action(self):
        return {JOANModules.DATA_RECORDER: DatarecorderAction,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerAction,
                JOANModules.HARDWARE_COMMUNICATION: HardwarecommunicationAction,
                JOANModules.CARLA_INTERFACE: SiminterfaceAction,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderAction}[self]

    @property
    def widget(self):
        return {JOANModules.DATA_RECORDER: DatarecorderWidget,
                JOANModules.FEED_BACK_CONTROLLER: FeedbackcontrollerWidget,
                JOANModules.HARDWARE_COMMUNICATION: HardwarecommunicationWidget,
                JOANModules.CARLA_INTERFACE: SiminterfaceWidget,
                JOANModules.TRAJECTORY_RECORDER: TrajectoryrecorderWidget}[self]

    def __str__(self):
        return {JOANModules.DATA_RECORDER: 'Data Recorder',
                JOANModules.FEED_BACK_CONTROLLER: 'Feed Back Controller',
                JOANModules.HARDWARE_COMMUNICATION: 'Hardware Communication',
                JOANModules.CARLA_INTERFACE: 'Carla Interface',
                JOANModules.TRAJECTORY_RECORDER: 'Trajectory Recorder'}[self]
