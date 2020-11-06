import enum
import os


class HapticControllerTypes(enum.Enum):
    """
    Enumeration class for all the different hardware types available. Contains:
    klass_mp: the class that runs in a seperate multiprocess which loops
    klass_dialog: the settings dialog of the input type
    shared_variables: the variables that need to be shared from the hardwareinpute type with the manager
    settings_ui_file: ui file of the settings dialog
    hardware_tab_uifile: ui file of the widget added in the module dialog
    settings: specific settings of the hardware input type
    __str__: the string represntation of the hardware input type

    """

    FDCA = 0
    FDCA_DUECA = 1

    @property
    def process(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerProcess
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontrollerdueca import FDCAControllerDuecaProcess

        return {HapticControllerTypes.FDCA: FDCAControllerProcess,
                HapticControllerTypes.FDCA_DUECA: FDCAControllerDuecaProcess
                }[self]

    @property
    def settings_dialog(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerSettingsDialog
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontrollerdueca import FDCAControllerDuecaSettingsDialog

        return {HapticControllerTypes.FDCA: FDCAControllerSettingsDialog,
                HapticControllerTypes.FDCA_DUECA: FDCAControllerDuecaSettingsDialog
                }[self]

    @property
    def shared_variables(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_sharedvalues import FDCASharedVariables
        from modules.hapticcontrollermanager.hapticcontrollermanager_sharedvalues import FDCADuecaSharedVariables

        return {HapticControllerTypes.FDCA: FDCASharedVariables,
                HapticControllerTypes.FDCA_DUECA: FDCADuecaSharedVariables
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
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontrollerdueca import FDCAControllerDuecaSettings

        return {HapticControllerTypes.FDCA: FDCAControllerSettings,
                HapticControllerTypes.FDCA_DUECA: FDCAControllerDuecaSettings
                }[self]

    def __str__(self):
        return {HapticControllerTypes.FDCA: 'FDCA',
                HapticControllerTypes.FDCA_DUECA: 'FDCA_Dueca'
                }[self]
