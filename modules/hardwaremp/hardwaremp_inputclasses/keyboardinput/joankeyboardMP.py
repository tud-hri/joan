import keyboard
from PyQt5 import QtWidgets, QtGui, uic

class JOANKeyboardMP():
    """
    Main class for the Keyboard input in a seperate multiprocess, this will loop!. Make sure that the things you do in this class are serializable, else
    it will fail.
    """

    def __init__(self, settings, shared_values):
        """
        Initializes the class
        :param hardware_manager_action:
        :param keyboard_tab:
        :param settings:
        """
        self.settings = settings
        
        self.settings_dialog = None
        self.shared_values = shared_values

        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False

        keyboard.hook(self.key_event, False)


    def key_event(self, key):
        """
        Distinguishes which key (that has been set before) is pressed and sets a boolean for the appropriate action.
        :param key:
        :return:
        """
        boolean_key_press_value = key.event_type == keyboard.KEY_DOWN
        int_key_identifier = QtGui.QKeySequence(key.name)[0]

        if int_key_identifier == self.settings['throttle_key']:
            self._throttle = boolean_key_press_value
        elif int_key_identifier == self.settings['brake_key']:
            self._brake = boolean_key_press_value
        elif int_key_identifier == self.settings['steer_left_key']:
            self._steer_left = boolean_key_press_value
            if boolean_key_press_value:
                self._steer_right = False
        elif int_key_identifier == self.settings['steer_right_key']:
            self._steer_right = boolean_key_press_value
            if boolean_key_press_value:
                self._steer_left = False
        elif int_key_identifier == self.settings['handbrake_key']:
            self._handbrake = boolean_key_press_value
        elif int_key_identifier == self.settings['reverse_key'] and boolean_key_press_value:
            self._reverse = not self._reverse

    def do(self):
        """
        Processes all the inputs of the keyboardinput and writes them to self._data which is then written to the news in the
        action class
        :return: self._data a dictionary containing :
            self.shared_values.brake = self.brake
            self.shared_values.throttle = self.throttle
            self.shared_values.steering_angle = self.steer
            self.shared_values.handbrake = self.handbrake
            self.shared_values.reverse = self.reverse
        """
        # Throttle:
        if self._throttle and self.shared_values.throttle < 1:
            self.shared_values.throttle = self.shared_values.throttle + (0.05 * self.settings['throttle_sensitivity'] / 100)
        elif self.shared_values.throttle > 0 and not self._throttle:
            self.shared_values.throttle = self.shared_values.throttle - (0.05 * self.settings['throttle_sensitivity'] / 100)
        elif self.shared_values.throttle < 0:
            self.shared_values.throttle = 0
        elif self.shared_values.throttle > 1:
            self.shared_values.throttle = 1

        # Brake:
        if self._brake and self.shared_values.brake < 1:
            self.shared_values.brake = self.shared_values.brake + (0.05 * self.settings['brake_sensitivity'] / 100)
        elif self.shared_values.brake > 0 and not self._brake:
            self.shared_values.brake = self.shared_values.brake - (0.05 * self.settings['brake_sensitivity'] / 100)
        elif self.shared_values.brake < 0:
            self.shared_values.brake = 0
        elif self.shared_values.brake > 1:
            self.shared_values.brake = 1

        # Steering:
        if self._steer_left and self.settings['max_steer'] >= self.shared_values.steering_angle >= self.settings['min_steer']:
            self.shared_values.steering_angle = self.shared_values.steering_angle - (self.settings['steer_sensitivity']/ 10000)
        elif self._steer_right and self.settings['min_steer'] <= self.shared_values.steering_angle <= self.settings['max_steer']:
            self.shared_values.steering_angle = self.shared_values.steering_angle + (self.settings['steer_sensitivity']/ 10000)
        elif self.shared_values.steering_angle > 0 and self.settings.auto_center:
            self.shared_values.steering_angle = self.shared_values.steering_angle - (self.settings['steer_sensitivity']/ 10000)
        elif self.shared_values.steering_angle < 0 and self.settings.auto_center:
            self.shared_values.steering_angle = self.shared_values.steering_angle + (self.settings['steer_sensitivity']/ 10000)

        if abs(self.shared_values.steering_angle) < self.settings['steer_sensitivity']/ 10000:
            self.shared_values.steering_angle = 0

        # Reverse
        self.shared_values.reverse = self._reverse



        # Handbrake
        self.shared_values.handbrake = self._handbrake
