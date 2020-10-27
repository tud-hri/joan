import enum
import os


class HardwareInputTypes(enum.Enum):
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

    KEYBOARD = 0
    JOYSTICK = 1
    SENSODRIVE = 2

    @property
    def klass_mp(self):
        from modules.hardwaremp.hardwaremp_inputclasses.joankeyboard import JOANKeyboardMP
        from modules.hardwaremp.hardwaremp_inputclasses.joanjoystick import JOANJoystickMP
        from modules.hardwaremp.hardwaremp_inputclasses.joansensodrive import JOANSensoDriveMP

        return {HardwareInputTypes.KEYBOARD: JOANKeyboardMP,
                HardwareInputTypes.JOYSTICK: JOANJoystickMP,
                HardwareInputTypes.SENSODRIVE: JOANSensoDriveMP
                }[self]

    @property
    def klass_dialog(self):
        from modules.hardwaremp.hardwaremp_inputclasses.joankeyboard import KeyBoardSettingsDialog
        from modules.hardwaremp.hardwaremp_inputclasses.joanjoystick import JoystickSettingsDialog
        from modules.hardwaremp.hardwaremp_inputclasses.joansensodrive import SensoDriveSettingsDialog

        return {HardwareInputTypes.KEYBOARD: KeyBoardSettingsDialog,
                HardwareInputTypes.JOYSTICK: JoystickSettingsDialog,
                HardwareInputTypes.SENSODRIVE: SensoDriveSettingsDialog
                }[self]

    @property
    def shared_variables(self):
        from modules.hardwaremp.hardwaremp_sharedvariables import KeyboardSharedVariables
        from modules.hardwaremp.hardwaremp_sharedvariables import JoystickSharedVariables
        from modules.hardwaremp.hardwaremp_sharedvariables import SensoDriveSharedVariables

        return {HardwareInputTypes.KEYBOARD: KeyboardSharedVariables,
                HardwareInputTypes.JOYSTICK: JoystickSharedVariables,
                HardwareInputTypes.SENSODRIVE: SensoDriveSharedVariables
                }[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremp_inputclasses/ui/")

        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "keyboard_settings_ui.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "joystick_settings_ui.ui"),
                HardwareInputTypes.SENSODRIVE: os.path.join(path_to_uis, "sensodrive_settings_ui.ui")
                }[self]

    @property
    def hardware_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremp_inputclasses/ui/")

        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "hardware_tab.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "hardware_tab.ui"),
                HardwareInputTypes.SENSODRIVE: os.path.join(path_to_uis, "hardware_tab_sensodrive.ui")
                }[self]

    @property
    def settings(self):
        from modules.hardwaremp.hardwaremp_settings import KeyBoardSettings
        from modules.hardwaremp.hardwaremp_settings import JoyStickSettings
        from modules.hardwaremp.hardwaremp_settings import SensoDriveSettings

        return {HardwareInputTypes.KEYBOARD: KeyBoardSettings,
                HardwareInputTypes.JOYSTICK: JoyStickSettings,
                HardwareInputTypes.SENSODRIVE: SensoDriveSettings
                }[self]

    def __str__(self):
        return {HardwareInputTypes.KEYBOARD: 'Keyboard',
                HardwareInputTypes.JOYSTICK: 'Joystick',
                HardwareInputTypes.SENSODRIVE: 'SensoDrive'
                }[self]
