import enum
import os


class NPCControllerTypes(enum.Enum):
    """
    Enumeration class for all the different NPC controller types available. Contains:
    process: the class that runs in a separate multiprocess which loops
    settings_dialog: the settings dialog of the controller
    shared_variables: the variables that need to be shared from the controller with the manager
    settings_ui_file: ui file of the settings dialog
    controller_tab_uifile: ui file of the widget added in the module dialog
    settings: specific settings of the controller
    __str__: the string representation of the controller

    """

    PURE_PURSUIT = 0
    FULL_THROTTLE = 1

    @property
    def process(self):
        from modules.npccontrollermanager.npc_controllers.purepursuit import PurePursuitControllerProcess
        from modules.npccontrollermanager.npc_controllers.full_throttle import FullThrottleControllerProcess

        return {NPCControllerTypes.PURE_PURSUIT: PurePursuitControllerProcess,
                NPCControllerTypes.FULL_THROTTLE: FullThrottleControllerProcess,
                }[self]

    @property
    def settings_dialog(self):
        from modules.npccontrollermanager.npc_controllers.purepursuit import PurePursuitSettingsDialog
        from modules.npccontrollermanager.npc_controllers.full_throttle import FullThrottleSettingsDialog

        return {NPCControllerTypes.PURE_PURSUIT: PurePursuitSettingsDialog,
                NPCControllerTypes.FULL_THROTTLE: FullThrottleSettingsDialog,
                }[self]

    @property
    def shared_variables(self):
        from modules.npccontrollermanager.npccontrollermanager_sharedvariables import NPCControllerSharedVariables

        return {NPCControllerTypes.PURE_PURSUIT: NPCControllerSharedVariables,
                NPCControllerTypes.FULL_THROTTLE: NPCControllerSharedVariables,
                }[self]

    @property
    def hardware_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "npc_controllers/ui/")

        return os.path.join(path_to_uis, "controller_tab.ui")

    @property
    def settings(self):
        from modules.npccontrollermanager.npc_controllers.purepursuit import PurePursuitSettings
        from modules.npccontrollermanager.npc_controllers.full_throttle import FullThrottleSettings

        return {NPCControllerTypes.PURE_PURSUIT: PurePursuitSettings,
                NPCControllerTypes.FULL_THROTTLE: FullThrottleSettings,
                }[self]

    def __str__(self):
        return {NPCControllerTypes.PURE_PURSUIT: "Pure Pursuit",
                NPCControllerTypes.FULL_THROTTLE: "Full Throttle",
                }[self]
