import enum
import os

from .hardwaremanagersettings import JoyStickSettings, SensoDriveSettings, KeyBoardSettings

class HardwareInputTypes(enum.Enum):
    """
    Enum to represent all available steering wheel controllers.
    """
    KEYBOARD= 0
    JOYSTICK = 1
    SENSODRIVE = 2

    @property
    def klass(self):
        from .inputclasses.joankeyboard import JOANKeyboard
        from .inputclasses.joanjoystick import JOANJoystick
        from .inputclasses.joansensodrive import JOANSensoDrive

        return {HardwareInputTypes.KEYBOARD: JOANKeyboard,
                HardwareInputTypes.JOYSTICK: JOANJoystick,
                HardwareInputTypes.SENSODRIVE: JOANSensoDrive}[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "inputclasses/ui/")
        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "keyboard_settings_ui.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "joystick_settings_ui.ui"),
                HardwareInputTypes.SENSODRIVE: os.path.join(path_to_uis, "sensodrive_settings_ui.ui")}[self]

    @property
    def hardware_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../dialog/")
        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "hardware_tab.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "hardware_tab.ui"),
                HardwareInputTypes.SENSODRIVE: os.path.join(path_to_uis, "hardware_tab_sensodrive.ui") }[self]

    @property
    def settings(self):
        return {HardwareInputTypes.KEYBOARD: KeyBoardSettings(),
                HardwareInputTypes.JOYSTICK: JoyStickSettings(),
                HardwareInputTypes.SENSODRIVE: SensoDriveSettings()}[self]

    def __str__(self):
        return {HardwareInputTypes.KEYBOARD: 'Keyboard',
                HardwareInputTypes.JOYSTICK: 'Joystick',
                HardwareInputTypes.SENSODRIVE: 'SensoDrive',}[self]
