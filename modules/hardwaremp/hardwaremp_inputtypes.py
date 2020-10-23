import enum
import os

from .hardwaremp_settings import KeyBoardSettings


class HardwareInputTypes(enum.Enum):
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
    def shared_values(self):
        from modules.hardwaremp.hardwaremp_sharedvalues import KeyboardSharedValues
        from modules.hardwaremp.hardwaremp_sharedvalues import JoystickSharedValues
        from modules.hardwaremp.hardwaremp_sharedvalues import SensoDriveSharedValues

        return {HardwareInputTypes.KEYBOARD: KeyboardSharedValues,
                HardwareInputTypes.JOYSTICK: JoystickSharedValues,
                HardwareInputTypes.SENSODRIVE: SensoDriveSharedValues
                }[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremp_inputclasses/ui/")

        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "keyboard_settings_ui.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "joystick_settings_ui.ui"),
                HardwareInputTypes.SENSODRIVE:  os.path.join(path_to_uis, "sensodrive_settings_ui.ui")
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

