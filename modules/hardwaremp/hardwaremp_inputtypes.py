import enum
import os

from .hardwaremp_settings import KeyBoardSettings


class HardwareInputTypes(enum.Enum):
    KEYBOARD = 0
    JOYSTICK = 1

    @property
    def klass(self):
        from modules.hardwaremp.hardwaremp_inputclasses.joankeyboard import JOANKeyboard
        from modules.hardwaremp.hardwaremp_inputclasses.joanjoystick import JOANJoystick

        return {HardwareInputTypes.KEYBOARD: JOANKeyboard,
                HardwareInputTypes.JOYSTICK: JOANJoystick
                }[self]

    @property
    def klass_mp(self):
        from modules.hardwaremp.hardwaremp_inputclasses.joankeyboard import JOANKeyboardMP
        from modules.hardwaremp.hardwaremp_inputclasses.joanjoystick import JOANJoystickMP

        return {HardwareInputTypes.KEYBOARD: JOANKeyboardMP,
                HardwareInputTypes.JOYSTICK: JOANJoystickMP
                }[self]

    @property
    def shared_values(self):
        from modules.hardwaremp.hardwaremp_sharedvalues import KeyboardSharedValues
        from modules.hardwaremp.hardwaremp_sharedvalues import JoystickSharedValues

        return {HardwareInputTypes.KEYBOARD: KeyboardSharedValues,
                HardwareInputTypes.JOYSTICK: JoystickSharedValues
                }[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremp_inputclasses/ui/")

        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "keyboard_settings_ui.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "joystick_settings_ui.ui")
                }[self]

    @property
    def hardware_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremp_inputclasses/ui/")

        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "hardware_tab.ui"),
                HardwareInputTypes.JOYSTICK: os.path.join(path_to_uis, "hardware_tab.ui")
                }[self]

    @property
    def settings(self):
        from modules.hardwaremp.hardwaremp_settings import KeyBoardSettings
        from modules.hardwaremp.hardwaremp_settings import JoyStickSettings

        return {HardwareInputTypes.KEYBOARD: KeyBoardSettings(),
                HardwareInputTypes.JOYSTICK: JoyStickSettings()
                }[self]

    def __str__(self):
        return {HardwareInputTypes.KEYBOARD: 'Keyboard',
                HardwareInputTypes.JOYSTICK: 'Joystick'
                }[self]
