from .transition import Transition


class SimplePrintTransition(Transition):
    """
    This in an example of a simple transition statement, which can be used in between two experiment conditions. This simple transition example just prints the
    names of the previous and next condition.
    """

    def execute_before_new_condition_activation(self, experiment, previous_condition):
        if previous_condition is not None:
            print('Transitioning from old condition: ' + previous_condition.name)
        else:
            print('Transitioning from the start of the experiment')

    def execute_after_new_condition_activation(self, experiment, next_condition):
        print('Applied settings corresponding to: ' + next_condition.name)

    @property
    def name(self):
        return 'Simple print transition'
