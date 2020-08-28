from .transition import Transition


class SimplePrintTransition(Transition):

    def execute_before_new_condition_activation(self, experiment, previous_condition):
        if previous_condition is not None:
            print('transitioning from old condition: ' + previous_condition.name)
        else:
            print('transitioning from the start of the experiment')

    def execute_after_new_condition_activation(self, experiment, next_condition):
        print('Applied settings corresponding to: ' + next_condition.name)

    @property
    def name(self):
        return 'Simple print transition'
