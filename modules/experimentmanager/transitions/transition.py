import abc


class Transition:
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
