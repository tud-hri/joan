import enum
import os


class HapticControllerTypes(enum.Enum):
    """
    Enumeration class for all the different hardware types available.
    """

    FDCA = 0

    @property
    def process(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerProcess

        return {HapticControllerTypes.FDCA: FDCAControllerProcess,
                }[self]

    @property
    def settings_dialog(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerSettingsDialog

        return {HapticControllerTypes.FDCA: FDCAControllerSettingsDialog,
                }[self]

    @property
    def shared_variables(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_sharedvariables import FDCASharedVariables

        return {HapticControllerTypes.FDCA: FDCASharedVariables,
                }[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hapticcontrollermanager_controllers/ui/")

        return {HapticControllerTypes.FDCA: os.path.join(path_to_uis, "fdca_settings_ui.ui"),
                HapticControllerTypes.FDCA_DUECA: os.path.join(path_to_uis, "fdcadueca_settings_ui.ui")
                }[self]

    @property
    def haptic_controller_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hapticcontrollermanager_controllers/ui/")

        return {HapticControllerTypes.FDCA: os.path.join(path_to_uis, "haptic_controller_tab.ui"),
                HapticControllerTypes.FDCA_DUECA: os.path.join(path_to_uis, "haptic_controller_tab.ui")
                }[self]

    @property
    def settings(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerSettings

        return {HapticControllerTypes.FDCA: FDCAControllerSettings,
                }[self]

    def __str__(self):
        return {HapticControllerTypes.FDCA: 'FDCA',
                HapticControllerTypes.FDCA_DUECA: 'FDCA_Dueca'
                }[self]
