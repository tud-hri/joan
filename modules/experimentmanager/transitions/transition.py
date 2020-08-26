import abc


class Transition:
    @staticmethod
    @abc.abstractmethod
    def execute_before_new_condition_activation(experiment, previous_condition):
        pass

    @staticmethod
    @abc.abstractmethod
    def execute_after_new_condition_activation(experiment, next_condition):
        pass

    @staticmethod
    @abc.abstractmethod
    def get_name():
        pass
