import enum
import os


class HardwareInputTypes(enum.Enum):
    """
    Enumeration class for all the different hardware types available. Contains:
    process: the class that runs in a seperate multiprocess which loops
    settings_dialog: the settings dialog of the input type
    shared_variables: the variables that need to be shared from the hardwareinpute type with the manager
    settings_ui_file: ui file of the settings dialog
    hardware_tab_uifile: ui file of the widget added in the module dialog
    settings: specific settings of the hardware input type
    __str__: the string represntation of the hardware input type

    """

    KEYBOARD = 0
    JOYSTICK = 1
    SENSODRIVE = 2
    LOGITECH_STEERING_WHEEL = 3

    @property
    def process(self):
        from modules.hardwaremanager.hardwaremanager_inputs.joankeyboard import JOANKeyboardProcess
        from modules.hardwaremanager.hardwaremanager_inputs.joanjoystick import JOANJoystickProcess
        from modules.hardwaremanager.hardwaremanager_inputs.joansensodrive import JOANSensoDriveProcess
        from modules.hardwaremanager.hardwaremanager_inputs.joanlogitech import JOANLogitechSteeringWheelProcess

        return {HardwareInputTypes.KEYBOARD: JOANKeyboardProcess,
                HardwareInputTypes.JOYSTICK: JOANJoystickProcess,
                HardwareInputTypes.SENSODRIVE: JOANSensoDriveProcess,
                HardwareInputTypes.LOGITECH_STEERING_WHEEL: JOANLogitechSteeringWheelProcess,
                }[self]

    @property
    def settings_dialog(self):
        from modules.hardwaremanager.hardwaremanager_inputs.joankeyboard import KeyBoardSettingsDialog
        from modules.hardwaremanager.hardwaremanager_inputs.joanjoystick import JoystickSettingsDialog
        from modules.hardwaremanager.hardwaremanager_inputs.joansensodrive import SensoDriveSettingsDialog
        from modules.hardwaremanager.hardwaremanager_inputs.joanlogitech import LogitechSteeringWheelSettingsDialog

        return {HardwareInputTypes.KEYBOARD: KeyBoardSettingsDialog,
                HardwareInputTypes.JOYSTICK: JoystickSettingsDialog,
                HardwareInputTypes.SENSODRIVE: SensoDriveSettingsDialog,
                HardwareInputTypes.LOGITECH_STEERING_WHEEL: LogitechSteeringWheelSettingsDialog
                }[self]

    @property
    def shared_variables(self):
        from modules.hardwaremanager.hardwaremanager_sharedvariables import GenericHardwareSharedVariables
        from modules.hardwaremanager.hardwaremanager_sharedvariables import SensoDriveSharedVariables

        return {HardwareInputTypes.KEYBOARD: GenericHardwareSharedVariables,
                HardwareInputTypes.JOYSTICK: GenericHardwareSharedVariables,
                HardwareInputTypes.SENSODRIVE: SensoDriveSharedVariables,
                HardwareInputTypes.LOGITECH_STEERING_WHEEL: GenericHardwareSharedVariables,
                }[self]

    @property
    def hardware_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremanager_inputs/ui/")

        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "hardware_tab.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "hardware_tab.ui"),
                HardwareInputTypes.SENSODRIVE: os.path.join(path_to_uis, "hardware_tab_sensodrive.ui"),
                HardwareInputTypes.LOGITECH_STEERING_WHEEL: os.path.join(path_to_uis, "hardware_tab.ui"),
                }[self]

    @property
    def settings(self):
        from modules.hardwaremanager.hardwaremanager_inputs.joankeyboard import KeyBoardSettings
        from modules.hardwaremanager.hardwaremanager_inputs.joanjoystick import JoyStickSettings
        from modules.hardwaremanager.hardwaremanager_inputs.joansensodrive import SensoDriveSettings
        from modules.hardwaremanager.hardwaremanager_inputs.joanlogitech import LogitechSteeringWheelSettings

        return {HardwareInputTypes.KEYBOARD: KeyBoardSettings,
                HardwareInputTypes.JOYSTICK: JoyStickSettings,
                HardwareInputTypes.SENSODRIVE: SensoDriveSettings,
                HardwareInputTypes.LOGITECH_STEERING_WHEEL: LogitechSteeringWheelSettings,
                }[self]

    def __str__(self):
        return {HardwareInputTypes.KEYBOARD: 'Keyboard',
                HardwareInputTypes.JOYSTICK: 'Joystick',
                HardwareInputTypes.SENSODRIVE: 'SensoDrive',
                HardwareInputTypes.LOGITECH_STEERING_WHEEL: 'Logitech Steering Wheel',
                }[self]
