import keyboard
from PyQt5 import QtGui

from core.module_process import ModuleProcess
from modules.joanmodules import JOANModules


class HardwareMPProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, start_event):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, start_event=start_event)

        self.shared_values = news.read_news(JOANModules.HARDWARE_MP)
        self.runtime_settings = {}  # same as 'self.input_classes = {}' from branch develop-joan2.0-develop-inputclass-in-mp from Joris

    def get_ready(self, runtime_settings):
        """
        Here, all runtime-settings are added to the already existing settings
        """
        # In branch develop-joan2.0-develop-inputclass-in-mp from Joris
        # if 'Keyboard' in items:
        #     self.input_classes[items] = HardwareInputTypes.KEYBOARD.MPklass(settings=self.settings['Hardware MP']['key_boards'][i],
        #                                                                     shared_values=self.inputs[items])
        # If all is right then the value is the choosen keyboard as an object

        # apply the settings here (e.g. create the hardware objects, etc, depending on the module's functionality
        self.runtime_settings = runtime_settings

        # add runtime-settigns to existing settings. Will not be saved to file
        
        
        # keyboard faken omdat onder iOS geen inputdevice verschijnt
        #from modules.hardwaremp.hardwaremp_inputtypes import KeyBoardSettings
        #t = KeyBoardSettings()

        for _, value in runtime_settings.items():
            # keyboard faken omdat onder iOS geen inputdevice verschijnt
            #value = t
            self._settings.append_hardware_input_device(value)
        if not self._settings.is_empty():
            self._settings = self._settings.as_dict()
            return True
        return False

        #keyboard.hook(self.key_event, False)

    def do_function(self):
        for _, value in self.runtime_settings.items():
            value.do()

    ''' TODO: remove this
    def key_event(self, key):
        """
        Distinguishes which key (that has been set before) is pressed and sets a boolean for the appropriate action.
        :param key:
        :return:
        """
        boolean_key_press_value = key.event_type == keyboard.KEY_DOWN
        int_key_identifier = QtGui.QKeySequence(key.name)[0]

        # if int_key_identifier == 87:
        #     self._throttle = boolean_key_press_value
        # elif int_key_identifier == 83:
        #     self._brake = boolean_key_press_value
        # elif int_key_identifier == 65:
        #     self._steer_left = boolean_key_press_value
        #     if boolean_key_press_value:
        #         self._steer_right = False
        # elif int_key_identifier == 68:
        #     self._steer_right = boolean_key_press_value
        #     if boolean_key_press_value:
        #         self._steer_left = False
        # elif int_key_identifier == 32:
        #     self._handbrake = boolean_key_press_value
        # elif int_key_identifier == 82 and boolean_key_press_value:
        #     self._reverse = not self._reverse

    def do(self):
        """
        Processes all the inputs of the keyboard and writes them to self._data which is then written to the news in the
        action class
        :return: self._data a dictionary containing :
            self.shared_values.brake = self.brake
            self.shared_values.throttle = self.throttle
            self.shared_values.steering_angle = self.steer
            self.shared_values.handbrake = self.handbrake
            self.shared_values.reverse = self.reverse
        """
        pass

        # # Throttle:
        # if self._throttle and self.shared_values.throttle < 1:
        #     self.shared_values.throttle = self.shared_values.throttle + (0.05 * 50 / 100)
        # elif self.shared_values.throttle > 0 and not self._throttle:
        #     self.shared_values.throttle = self.shared_values.throttle - (0.05 * 50 / 100)
        # elif self.shared_values.throttle < 0:
        #     self.shared_values.throttle = 0
        # elif self.shared_values.throttle > 1:
        #     self.shared_values.throttle = 1
        #
        # # Brake:
        # if self._brake and self.shared_values.brake < 1:
        #     self.shared_values.brake = self.shared_values.brake + (0.05 * 50 / 100)
        # elif self.shared_values.brake > 0 and not self._brake:
        #     self.shared_values.brake = self.shared_values.brake - (0.05 * 50 / 100)
        # elif self.shared_values.brake < 0:
        #     self.shared_values.brake = 0
        # elif self.shared_values.brake > 1:
        #     self.shared_values.brake = 1
        #
        # # Steering:
        # if self._steer_left and 1.57 >= self.shared_values.steering_angle >= -1.57:
        #     self.shared_values.steering_angle = self.shared_values.steering_angle - (50 / 10000)
        # elif self._steer_right and -1.57 <= self.shared_values.steering_angle <= 1.57:
        #     self.shared_values.steering_angle = self.shared_values.steering_angle + (50 / 10000)
        # elif self.shared_values.steering_angle > 0:
        #     self.shared_values.steering_angle = self.shared_values.steering_angle - (50 / 10000)
        # elif self.shared_values.steering_angle < 0:
        #     self.shared_values.steering_angle = self.shared_values.steering_angle + (50 / 10000)
        #
        # if abs(self.shared_values.steering_angle) < 50 / 10000:
        #     self.shared_values.steering_angle = 0
        #
        # # Reverse
        # self.shared_values.reverse = self._reverse
        #
        # # Handbrake
        # self.shared_values.handbrake = self._handbrake
    '''