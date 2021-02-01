from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class ControllerPlotterManager(ModuleManager):
    """
    Creates a window that plots relevant parameters of a haptic shared controller (FDCA)
    """

    def __init__(self, news, central_settings, signals, central_state_monitor, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.CONTROLLER_PLOTTER, news=news, central_settings=central_settings, signals=signals,
                         central_state_monitor=central_state_monitor, time_step_in_ms=time_step_in_ms, parent=parent)

    def initialize(self):
        self.module_dialog.initialize()
        super().initialize()

    def stop(self):
        # Clear graphs when stopping module
        self.module_dialog.module_widget.top_view_graph.clear()
        self.module_dialog.module_widget.torque_graph.clear()
        self.module_dialog.module_widget.errors_graph.clear()
        self.module_dialog.module_widget.fb_torques_graph.clear()
        self.module_dialog.module_widget.sw_graph.clear()

        self.module_dialog.top_view_legend.clear()
        self.module_dialog.torque_legend.clear()
        self.module_dialog.torques_legend.clear()
        self.module_dialog.errors_legend.clear()
        self.module_dialog.sw_legend.clear()

        return super().stop()
