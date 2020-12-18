import abc


class Transition:
    """
    A transition object describes the actions to be taken in between experiment conditions. Two methods can be defined, one that is executed before the new
    condition activation and one after the activation. All transition objects should have a property that represents the name of the transition.

    For an example please have a look at SimplePrintTransition in .printtransition.py
    """
    @abc.abstractmethod
    def execute_before_new_condition_activation(self, experiment, previous_condition):
        pass

    @abc.abstractmethod
    def execute_after_new_condition_activation(self, experiment, next_condition):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass
