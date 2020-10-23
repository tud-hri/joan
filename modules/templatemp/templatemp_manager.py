from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules


class TemplateMPManager(ModuleManager):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.TEMPLATE_MP, time_step_in_ms=time_step_in_ms, parent=parent)

    def initialize(self):
        """
        Example of adding an 'adjustable setting' to the self.shared_variables. For example, we added a variable 'overwrite_with_current_time' in
        shared variables, which is also a variable in settings.
        The settings variable will serve as an initial value for the shared variable, which can be changed during RUNNING. The settings value is not changed.
        :return:
        """
        super().initialize()

        # update value in self.shared_variables with the value in settings
        # self.shared_variables.overwrite_with_current_time = self.module_settings.overwrite_with_current_time
