from .transition import Transition


class SimplePrintTransition(Transition):

    @staticmethod
    def execute_before_new_condition_activation(experiment, previous_condition):
        print('transitioning from old condition: ' + previous_condition.name)

    @staticmethod
    def execute_after_new_condition_activation(experiment, next_condition):
        print('Applied settings corresponding to: ' + next_condition.name)

    @staticmethod
    def get_name():
        return 'Simple print transition'
