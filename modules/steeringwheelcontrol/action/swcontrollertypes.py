import enum
import os
from .steeringwheelcontrolsettings import PDcontrollerSettings, FDCAcontrollerSettings, ManualcontrollerSettings

class SWControllerTypes(enum.Enum):
    """
    Enum to represent all available steering wheel controllers.
    """
    MANUAL = 0
    PD_SWCONTROLLER = 1
    FDCA_SWCONTROLLER = 2

    @property
    def klass(self):
        from .swcontrollers.manualswcontroller import ManualSWController
        from .swcontrollers.pdswcontroller import PDSWController
        from .swcontrollers.fdcaswcontroller import FDCASWController

        return {SWControllerTypes.MANUAL: ManualSWController,
                SWControllerTypes.PD_SWCONTROLLER: PDSWController,
                SWControllerTypes.FDCA_SWCONTROLLER: FDCASWController}[self]

    @property
    def tuning_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "swcontrollers/ui/")
        return {SWControllerTypes.MANUAL: os.path.join(path_to_uis, "manual_tab.ui"),
                SWControllerTypes.PD_SWCONTROLLER: os.path.join(path_to_uis, "pd_settings_ui.ui"),
                SWControllerTypes.FDCA_SWCONTROLLER: os.path.join(path_to_uis, "fdca_tab.ui")}[self]

    @property
    def controller_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dialog/")
        return {SWControllerTypes.MANUAL: os.path.join(path_to_uis, "sw_controller_tab.ui"),
                SWControllerTypes.PD_SWCONTROLLER: os.path.join(path_to_uis, "sw_controller_tab.ui"),
                SWControllerTypes.FDCA_SWCONTROLLER: os.path.join(path_to_uis, "sw_controller_tab.ui")}[self]

    @property
    def settings(self):
        return{SWControllerTypes.MANUAL: ManualcontrollerSettings(),
               SWControllerTypes.PD_SWCONTROLLER: PDcontrollerSettings(),
               SWControllerTypes.FDCA_SWCONTROLLER: FDCAcontrollerSettings()}[self]

    def __str__(self):
        return {SWControllerTypes.MANUAL: 'Manual',
                SWControllerTypes.PD_SWCONTROLLER: 'PD',
                SWControllerTypes.FDCA_SWCONTROLLER: 'FDCA'}[self]
