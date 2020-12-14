import os
import copy

from PyQt5 import QtWidgets, QtCore, QtGui

from modules.experimentmanager.condition import Condition
from modules.experimentmanager.experiment import Experiment
from modules.experimentmanager.transitions import TransitionsList
from .edit_experiment_dialog_ui import Ui_ExperimentManagerWidget
from .previewconditiondialog import PreviewConditionDialog
from core.statesenum import State

class EditExperimentDialog(QtWidgets.QDialog):
    def __init__(self, experiment: Experiment, experiment_save_path, settings_singleton, parent=None):
        super().__init__(parent)

        self.manager = parent.module_manager
        self.manager.central_state_monitor.add_combined_state_change_listener(self._update_enabled_buttons)
        self.experiment = experiment
        self.experiment_save_path = experiment_save_path
        self.singleton_settings = settings_singleton

        self.ui = Ui_ExperimentManagerWidget()
        self.ui.setupUi(self)

        self.ui.saveExperimentPushButton.clicked.connect(self.accept)
        self.ui.modulesIncludedListWidget.currentItemChanged.connect(self._update_base_settings_tree)
        self.ui.baseSettingsTreeWidget.itemDoubleClicked.connect(self._edit_setting)
        self.ui.createConditionPushButton.clicked.connect(self.create_new_available_condition)
        self.ui.addConditionPushButton.clicked.connect(self.add_condition_to_sequence)
        self.ui.removeConditionPushButton.clicked.connect(self.remove_from_sequence)
        self.ui.addTransitionPushButton.clicked.connect(self.add_transition_to_sequence)
        self.ui.removeTransitionPushButton.clicked.connect(self.remove_from_sequence)
        self.ui.conditionUpPushButton.clicked.connect(self.move_condition_up)
        self.ui.conditionDownPushButton.clicked.connect(self.move_condition_down)
        self.ui.deleteAvailableConditionPushButton.clicked.connect(self.delete_available_condition)
        self.ui.availableConditionsListWidget.itemSelectionChanged.connect(self._update_enabled_buttons)
        self.ui.currentConditionsListWidget.itemSelectionChanged.connect(self._update_enabled_buttons)
        self.ui.availableTransitionsListWidget.itemSelectionChanged.connect(self._update_enabled_buttons)
        self.ui.availableConditionsListWidget.itemDoubleClicked.connect(self._preview_condition)

        self.ui.experimentNameLineEdit.setText(os.path.abspath(self.experiment_save_path).split('\\')[-1])

        for module in self.experiment.modules_included:
            item = QtWidgets.QListWidgetItem(str(module))
            item.setData(QtCore.Qt.UserRole, module)
            self.ui.modulesIncludedListWidget.addItem(item)

        for transition in TransitionsList():
            item = QtWidgets.QListWidgetItem(transition.name)
            item.setData(QtCore.Qt.UserRole, transition)
            self.ui.availableTransitionsListWidget.addItem(item)

        self._all_conditions = copy.copy(self.experiment.all_conditions)
        self._active_condition_sequence = copy.copy(self.experiment.active_condition_sequence)
        self._base_settings = copy.deepcopy(experiment.base_settings)

        self._update_enabled_buttons()
        self.update_condition_lists()

        self.show()



    def accept(self):
        self.experiment.all_conditions = self._all_conditions
        self.experiment.active_condition_sequence = self._active_condition_sequence
        self.experiment.base_settings = self._base_settings

        self.experiment.save_to_file(self.experiment_save_path)
        super().accept()

    def create_new_available_condition(self):
        condition_name, accepted = QtWidgets.QInputDialog.getText(self, 'New condition', 'What is the name of this condition?')
        if accepted:
            condition_name = condition_name.strip()
            if not condition_name:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'New condition could not be created because no name was provided.')
            elif condition_name in [c.name for c in self._all_conditions]:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'New condition could not be created because a condition with this name already exists.')
            else:
                new_condition = Condition.set_from_current_settings(condition_name, self.experiment, self.singleton_settings)
                self._all_conditions.append(new_condition)
                self.update_condition_lists()

    def delete_available_condition(self):
        selected_condition = self.ui.availableConditionsListWidget.currentItem().data(QtCore.Qt.UserRole)
        if selected_condition in self._active_condition_sequence:
            answer = QtWidgets.QMessageBox.question(self, 'Waring', 'The condition you are trying to remove is used in the experiments condition sequence. '
                                                                    'do you want to go ahead and also remove it from the sequence?')
            if answer == QtWidgets.QMessageBox.No:
                return
            else:
                while selected_condition in self._active_condition_sequence:
                    self._active_condition_sequence.remove(selected_condition)
                self.update_condition_lists()
        self._all_conditions.remove(selected_condition)
        self.update_condition_lists()

    def add_condition_to_sequence(self):
        selected_condition = self.ui.availableConditionsListWidget.currentItem().data(QtCore.Qt.UserRole)
        self._active_condition_sequence.append(selected_condition)
        self.update_condition_lists()

    def remove_from_sequence(self):
        selected_condition = self.ui.currentConditionsListWidget.currentRow()
        self._active_condition_sequence.pop(selected_condition)
        self.update_condition_lists()

    def add_transition_to_sequence(self):
        selected_transition = self.ui.availableTransitionsListWidget.currentItem().data(QtCore.Qt.UserRole)
        self._active_condition_sequence.append(selected_transition)
        self.update_condition_lists()

    def move_condition_up(self):
        old_index = self.ui.currentConditionsListWidget.currentRow()
        self.ui.currentConditionsListWidget.insertItem(old_index - 1, self.ui.currentConditionsListWidget.takeItem(old_index))
        self.ui.currentConditionsListWidget.setCurrentRow(old_index - 1)
        new_sequence = [self.ui.currentConditionsListWidget.item(index).data(QtCore.Qt.UserRole) for index in
                        range(self.ui.currentConditionsListWidget.count())]

        self._active_condition_sequence = new_sequence.copy()

    def move_condition_down(self):
        old_index = self.ui.currentConditionsListWidget.currentRow()
        self.ui.currentConditionsListWidget.insertItem(old_index + 1, self.ui.currentConditionsListWidget.takeItem(old_index))
        self.ui.currentConditionsListWidget.setCurrentRow(old_index + 1)
        new_sequence = [self.ui.currentConditionsListWidget.item(index).data(QtCore.Qt.UserRole) for index in
                        range(self.ui.currentConditionsListWidget.count())]
        self._active_condition_sequence = new_sequence.copy()

    def _preview_condition(self, list_item):
        condition = list_item.data(QtCore.Qt.UserRole)
        PreviewConditionDialog(condition, self)

    def _update_enabled_buttons(self):
        if self.manager.central_state_monitor.combined_state == State.INITIALIZED:
            self.ui.createConditionPushButton.setEnabled(True)
        else:
            self.ui.createConditionPushButton.setEnabled(False)

        if bool(self.ui.currentConditionsListWidget.currentItem()):
            selected_current_is_condition = isinstance(self.ui.currentConditionsListWidget.currentItem().data(QtCore.Qt.UserRole), Condition)
            selected_current_is_transition = not selected_current_is_condition
        else:
            selected_current_is_condition = False
            selected_current_is_transition = False

        self.ui.addConditionPushButton.setEnabled(bool(self.ui.availableConditionsListWidget.currentRow() != -1))
        self.ui.removeConditionPushButton.setEnabled(selected_current_is_condition)

        self.ui.addTransitionPushButton.setEnabled(bool(self.ui.availableTransitionsListWidget.currentRow() != -1))
        self.ui.removeTransitionPushButton.setEnabled(selected_current_is_transition)

        self.ui.conditionUpPushButton.setEnabled(bool(self.ui.currentConditionsListWidget.currentRow() != -1))
        self.ui.conditionDownPushButton.setEnabled(bool(self.ui.currentConditionsListWidget.currentRow() != -1))

        self.ui.deleteAvailableConditionPushButton.setEnabled(bool(self.ui.availableConditionsListWidget.currentRow() != -1))

    def update_condition_lists(self):
        self.ui.availableConditionsListWidget.clear()
        self.ui.currentConditionsListWidget.clear()

        for condition in self._all_conditions:
            item = QtWidgets.QListWidgetItem(condition.name)
            item.setData(QtCore.Qt.UserRole, condition)
            self.ui.availableConditionsListWidget.addItem(item)

        for condition_or_transition in self._active_condition_sequence:
            item = QtWidgets.QListWidgetItem(condition_or_transition.name)
            item.setData(QtCore.Qt.UserRole, condition_or_transition)
            if not isinstance(condition_or_transition, Condition):
                item.setBackground(QtGui.QBrush(QtGui.QColor(200, 100, 200, 50)))
            self.ui.currentConditionsListWidget.addItem(item)

        self._update_enabled_buttons()

    def _update_base_settings_tree(self):
        self.ui.baseSettingsTreeWidget.clear()

        if self.ui.modulesIncludedListWidget.currentItem():
            self.ui.baseSettingsTreeWidget.setEnabled(True)

            selected_module = self.ui.modulesIncludedListWidget.currentItem().data(QtCore.Qt.UserRole)
            settings_to_display = self._base_settings[selected_module]
            for key, value in settings_to_display.items():
                self._create_tree_item(self.ui.baseSettingsTreeWidget, key, value)
        else:
            self.ui.baseSettingsTreeWidget.setEnabled(False)

    def _edit_setting(self, item):
        key = item.data(0, 0)
        value = item.data(1, 0)
        if value is not None:
            if type(value) == int:
                new_value, is_accepted = QtWidgets.QInputDialog.getInt(self, key, key, value)
            elif type(value) == float:
                new_value, is_accepted = QtWidgets.QInputDialog.getDouble(self, key, key, value)
            elif type(value) == str:
                new_value, is_accepted = QtWidgets.QInputDialog.getText(self, key, key, text=value)
            else:
                new_value, is_accepted = None, False

            if is_accepted:
                key_sequence = self._find_key_sequence(item, [])
                selected_module = self.ui.modulesIncludedListWidget.currentItem().data(QtCore.Qt.UserRole)
                parent_setting_object = self._base_settings[selected_module]

                for inner_key in key_sequence:
                    if isinstance(parent_setting_object, dict) or type(inner_key) == int:
                        parent_setting_object = parent_setting_object[inner_key]
                    else:
                        parent_setting_object = parent_setting_object.__getattribute__(inner_key)

                if isinstance(parent_setting_object, dict):
                    parent_setting_object[key] = new_value
                else:
                    parent_setting_object.__setattr__(key, new_value)

                self._update_base_settings_tree()

    @staticmethod
    def _find_key_sequence(tree_item, key_list):
        if tree_item.parent() is None:
            return key_list
        else:
            key_list.insert(0, tree_item.parent().data(0, 0))
            return EditExperimentDialog._find_key_sequence(tree_item.parent(), key_list)

    @staticmethod
    def _create_tree_item(parent, key, value):
        if isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, key)

            for inner_key, inner_value in value.items():
                EditExperimentDialog._create_tree_item(item, inner_key, inner_value)
            return item
        if isinstance(value, list):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, key)

            for index, inner_value in enumerate(value):
                EditExperimentDialog._create_tree_item(item, index, inner_value)
            return item
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, key)
            item.setData(1, 0, value)
            return item
