import os

from PyQt5 import QtWidgets

from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from .condition import Condition
from .experiment import Experiment
import copy
from core.statesenum import State


class ExperimentManager(ModuleManager):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """
    current_experiment: Experiment

    def __init__(self, news, central_settings, signals, time_step_in_ms=10, parent=None):
        """

        :param news:
        :param signals:
        :param time_step_in_ms:
        :param parent:
        """
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, news=news, central_settings=central_settings, signals=signals, time_step_in_ms=time_step_in_ms,
                         use_state_machine_and_process=False, parent=parent)
        # create/get default experiment_settings
        self.current_experiment = None

        cur_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(os.path.dirname(cur_path)))
        self.experiment_save_path = os.path.join(path, 'experiments/')

        self.active_condition = None
        self.active_condition_index = None

    def create_new_experiment(self, modules_to_include, save_path):
        """

        :param modules_to_include:
        :param save_path:
        :return:
        """
        # create the experiment
        self.current_experiment = Experiment(modules_to_include)
        self.current_experiment.set_from_current_settings(self.singleton_settings)
        self.experiment_save_path = save_path
        self.save_experiment()

        # update the gui
        self.module_dialog.update_gui()
        self.module_dialog.update_condition_lists()

        # and open the experiment dialog
        self.module_dialog.open_experiment_dialog()

    def save_experiment(self):
        """

        :return:
        """
        if self.current_experiment:
            self.current_experiment.save_to_file(self.experiment_save_path)

    def load_experiment(self, file_path):
        """

        :param file_path:
        :return:
        """
        self.experiment_save_path = file_path
        self.current_experiment = Experiment.load_from_file(file_path)
        self.module_dialog.update_gui()
        self.module_dialog.update_condition_lists()

    def activate_selected_condition(self, condition, condition_index):
        """
        To activate the condition, send the settings to the corresponding module (settings)
        :param condition:
        :param condition_index: self-explanatory
        :return:
        """
        for module, base_settings_dict in self.current_experiment.base_settings.items():
            module_settings_dict = copy.deepcopy(base_settings_dict)
            self._recursively_copy_dict(condition.diff[module], module_settings_dict)
            self.singleton_settings.get_settings(module).load_from_dict({str(module): module_settings_dict})

        self.active_condition = condition
        self.active_condition_index = condition_index

        for signal in self.signals.all_signals:
            self.signals.all_signals[signal].emit()

        return True

    def transition_to_next_condition(self):
        """

        :return:
        """
        if not self.current_experiment:
            return False

        if not self.active_condition:
            self.active_condition_index = -1
        try:
            next_condition_or_transition = self.current_experiment.active_condition_sequence[self.active_condition_index + 1]
            if isinstance(next_condition_or_transition, Condition):
                return self.activate_selected_condition(next_condition_or_transition, self.active_condition_index + 1)
            else:
                transition = next_condition_or_transition
                transition.execute_before_new_condition_activation(self.current_experiment, self.active_condition)

                # search for the next condition
                added_index = 1
                while not isinstance(next_condition_or_transition, Condition):
                    try:
                        added_index += 1
                        next_condition_or_transition = self.current_experiment.active_condition_sequence[self.active_condition_index + added_index]
                    except IndexError:
                        # end of the list of conditions and transitions
                        return True
                    finally:
                        if added_index > 2:
                            QtWidgets.QMessageBox.warning(self.module_dialog, 'Warning', 'A sequence of multiple consecutive transitions was found. '
                                                                                         'This is illegal, only the first was executed, the others were '
                                                                                         'ignored.')

                if self.activate_selected_condition(next_condition_or_transition, self.active_condition_index + added_index):
                    transition.execute_after_new_condition_activation(self.current_experiment, self.active_condition)
                    return True
                else:
                    return False
        except IndexError:
            return False

    @staticmethod
    def _recursively_copy_dict(source, destination):
        for key, item in source.items():
            if isinstance(item, dict):
                try:
                    ExperimentManager._recursively_copy_dict(item, destination[key])
                except KeyError:
                    destination[key] = {}
                    ExperimentManager._recursively_copy_dict(item, destination[key])
            else:
                if item:  # check to avoid empty source list copying over filled destination list.
                    destination[key] = item
