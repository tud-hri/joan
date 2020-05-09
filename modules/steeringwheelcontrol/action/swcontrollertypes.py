import enum
import os


class SWContollerTypes(enum.Enum):
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

        return {SWContollerTypes.MANUAL: ManualSWController,
                SWContollerTypes.PD_SWCONTROLLER: PDSWController,
                SWContollerTypes.FDCA_SWCONTROLLER: FDCASWController}[self]

    @property
    def tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "swcontrollers/ui/")
        return {SWContollerTypes.MANUAL: os.path.join(path_to_uis, "manual_tab.ui"),
                SWContollerTypes.PD_SWCONTROLLER: os.path.join(path_to_uis, "pd_tab.ui"),
                SWContollerTypes.FDCA_SWCONTROLLER: os.path.join(path_to_uis, "fdca_tab.ui")}[self]

    def __str__(self):
        return {SWContollerTypes.MANUAL: 'Manual',
                SWContollerTypes.PD_SWCONTROLLER: 'PD',
                SWContollerTypes.FDCA_SWCONTROLLER: 'FDCA'}[self]
