import enum
import os


class HapticControllerTypes(enum.Enum):
    """
    Enumeration class for all the different hardware types available.
    """

    FDCA = 0
    TRADED_CONTROL = 1


    @property
    def process(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerProcess
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.tradedcontroller import TradedControllerProcess

        return {HapticControllerTypes.FDCA: FDCAControllerProcess,
                HapticControllerTypes.TRADED_CONTROL: TradedControllerProcess,
                }[self]

    @property
    def settings_dialog(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerSettingsDialog
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.tradedcontroller import TradedControllerSettingsDialog

        return {HapticControllerTypes.FDCA: FDCAControllerSettingsDialog,
                HapticControllerTypes.TRADED_CONTROL: TradedControllerSettingsDialog,
                }[self]

    @property
    def shared_variables(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_sharedvariables import FDCASharedVariables
        from modules.hapticcontrollermanager.hapticcontrollermanager_sharedvariables import TradedControllerSharedVariables

        return {HapticControllerTypes.FDCA: FDCASharedVariables,
                HapticControllerTypes.TRADED_CONTROL: TradedControllerSharedVariables,
                }[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hapticcontrollermanager_controllers/ui/")

        return {HapticControllerTypes.FDCA: os.path.join(path_to_uis, "fdca_settings_ui.ui"),
                HapticControllerTypes.TRADED_CONTROL: os.path.join(path_to_uis, "tradedcontroller_settings_ui.ui"),
                }[self]

    @property
    def haptic_controller_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hapticcontrollermanager_controllers/ui/")

        return {HapticControllerTypes.FDCA: os.path.join(path_to_uis, "haptic_controller_tab.ui"),
                HapticControllerTypes.TRADED_CONTROL: os.path.join(path_to_uis, "traded_controller_tab.ui"),
                }[self]

    @property
    def settings(self):
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.fdcacontroller import FDCAControllerSettings
        from modules.hapticcontrollermanager.hapticcontrollermanager_controllers.tradedcontroller import TradedControllerSettings

        return {HapticControllerTypes.FDCA: FDCAControllerSettings,
                HapticControllerTypes.TRADED_CONTROL: TradedControllerSettings,
                }[self]

    def __str__(self):
        return {HapticControllerTypes.FDCA: 'Four Design Choices Architecture',
                HapticControllerTypes.TRADED_CONTROL: 'Traded Control'
                }[self]
