import os

from PyQt5 import QtWidgets, QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from process.joanmoduledialog import JoanModuleDialog
from .newexperimentdialog import NewExperimentDialog
from .previewconditiondialog import PreviewConditionDialog


class ExperimentManagerDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, parent=None):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, module_action=module_action, use_state_machine_and_timer=False, parent=parent)

        self.module_widget.initializeExperimentPushButton.clicked.connect(self.initialize_new_experiment)
        self.module_widget.saveExperimentPushButton.clicked.connect(self.save_experiment)
        self.module_widget.loadExperimentPushButton.clicked.connect(self.load_experiment)

        self.module_widget.modulesIncludedListWidget.currentItemChanged.connect(self._update_base_settings_tree)
        self.module_widget.baseSettingsTreeWidget.itemDoubleClicked.connect(self._edit_setting)
        self.module_widget.createConditionPushButton.clicked.connect(self.create_new_condition)
        self.module_widget.addConditionPushButton.clicked.connect(self.add_condition)
        self.module_widget.removeConditionPushButton.clicked.connect(self.remove_condition)
        self.module_widget.conditionUpPushButton.clicked.connect(self.condition_up)
        self.module_widget.conditionDownPushButton.clicked.connect(self.condition_down)

        self.module_widget.availableConditionsListWidget.itemSelectionChanged.connect(self._update_enabled_condition_buttons)
        self.module_widget.currentConditionsListWidget.itemSelectionChanged.connect(self._update_enabled_condition_buttons)

        self.module_widget.availableConditionsListWidget.itemDoubleClicked.connect(self._preview_condition)

        self.module_widget.activateConditionPushButton.clicked.connect(self.activate_condition)

        self.update_gui()
        self._update_enabled_condition_buttons()
        self.update_condition_lists()

    def initialize_new_experiment(self):
        new_experiment_dialog = NewExperimentDialog(self.module_action.singleton_settings.all_settings_keys, parent=self)
        new_experiment_dialog.accepted.connect(
            lambda: self.module_action.initialize_new_experiment(new_experiment_dialog.modules_to_include, new_experiment_dialog.file_path))

    def create_new_condition(self):
        condition_name, accepted = QtWidgets.QInputDialog.getText(self, 'New condition', 'What is the name of this condition?')
        if accepted:
            if not condition_name:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'New condition could not be created because no name was provided.')
            else:
                try:
                    self.module_action.create_new_condition(condition_name)
                except ValueError as e:
                    QtWidgets.QMessageBox.warning(self, 'Warning', str(e))

    def add_condition(self):
        selected_condition = self.module_widget.availableConditionsListWidget.currentItem().data(0)
        self.module_action.add_condition(selected_condition)

    def remove_condition(self):
        selected_condition = self.module_widget.currentConditionsListWidget.currentRow()
        self.module_action.remove_condition(selected_condition)

    def condition_up(self):
        old_index = self.module_widget.currentConditionsListWidget.currentRow()
        self.module_widget.currentConditionsListWidget.insertItem(old_index - 1, self.module_widget.currentConditionsListWidget.takeItem(old_index))
        self.module_widget.currentConditionsListWidget.setCurrentRow(old_index - 1)
        new_sequence = [self.module_widget.currentConditionsListWidget.item(index).data(0) for index in range(self.module_widget.currentConditionsListWidget.count())]
        self.module_action.update_condition_sequence(new_sequence)

    def condition_down(self):
        old_index = self.module_widget.currentConditionsListWidget.currentRow()
        self.module_widget.currentConditionsListWidget.insertItem(old_index + 1, self.module_widget.currentConditionsListWidget.takeItem(old_index))
        self.module_widget.currentConditionsListWidget.setCurrentRow(old_index + 1)
        new_sequence = [self.module_widget.currentConditionsListWidget.item(index).data(0) for index in range(self.module_widget.currentConditionsListWidget.count())]
        self.module_action.update_condition_sequence(new_sequence)

    def load_experiment(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Experiment', filter='JSON (*.json)')
        if file_path:
            self.module_action.load_experiment(file_path)

    def save_experiment(self):
        self.module_action.save_experiment()

    def _preview_condition(self, list_item):
        condition = list_item.data(QtCore.Qt.UserRole)
        PreviewConditionDialog(condition, self)

    def _update_enabled_condition_buttons(self):
        self.module_widget.addConditionPushButton.setEnabled(bool(self.module_widget.availableConditionsListWidget.currentRow() != -1))
        self.module_widget.removeConditionPushButton.setEnabled(bool(self.module_widget.currentConditionsListWidget.currentRow() != -1))
        self.module_widget.conditionUpPushButton.setEnabled(bool(self.module_widget.currentConditionsListWidget.currentRow() != -1))
        self.module_widget.conditionDownPushButton.setEnabled(bool(self.module_widget.currentConditionsListWidget.currentRow() != -1))
        self.module_widget.activateConditionPushButton.setEnabled(bool(self.module_widget.currentConditionsListWidget.currentRow() != -1))

    def update_gui(self):
        self.module_widget.modulesIncludedListWidget.clear()

        self.module_widget.modulesIncludedListWidget.setEnabled(bool(self.module_action.current_experiment))
        self.module_widget.baseSettingsTreeWidget.setEnabled(bool(self.module_action.current_experiment))
        self.module_widget.currentConditionsListWidget.setEnabled(bool(self.module_action.current_experiment))
        self.module_widget.availableConditionsListWidget.setEnabled(bool(self.module_action.current_experiment))
        self.module_widget.createConditionPushButton.setEnabled(bool(self.module_action.current_experiment))

        if self.module_action.current_experiment:
            self.module_widget.experimentNameLineEdit.setText(os.path.abspath(self.module_action.experiment_save_path).split('\\')[-1])

            for module in self.module_action.current_experiment.modules_included:
                item = QtWidgets.QListWidgetItem(str(module))
                item.setData(QtCore.Qt.UserRole, module)
                self.module_widget.modulesIncludedListWidget.addItem(item)
        else:
            self.module_widget.experimentNameLineEdit.setText('-')

    def update_condition_lists(self):
        self.module_widget.availableConditionsListWidget.clear()
        self.module_widget.currentConditionsListWidget.clear()

        if self.module_action.current_experiment:
            self.module_widget.currentConditionsListWidget.setEnabled(True)
            self.module_widget.availableConditionsListWidget.setEnabled(True)

            for condition in self.module_action.current_experiment.all_conditions:
                item = QtWidgets.QListWidgetItem(condition.name)
                item.setData(QtCore.Qt.UserRole, condition)
                self.module_widget.availableConditionsListWidget.addItem(item)

            for condition_name in self.module_action.current_experiment.active_condition_sequence:
                item = QtWidgets.QListWidgetItem(condition_name)
                self.module_widget.currentConditionsListWidget.addItem(item)
        else:
            self.module_widget.currentConditionsListWidget.setEnabled(False)
            self.module_widget.availableConditionsListWidget.setEnabled(False)
        self._update_enabled_condition_buttons()

    def activate_condition(self):
        current_condition = self.module_widget.currentConditionsListWidget.item(0)
        self.module_action.activate_condition(current_condition)

    def _update_base_settings_tree(self):
        self.module_widget.baseSettingsTreeWidget.clear()

        if self.module_widget.modulesIncludedListWidget.currentItem():
            self.module_widget.baseSettingsTreeWidget.setEnabled(True)

            selected_module = self.module_widget.modulesIncludedListWidget.currentItem().data(QtCore.Qt.UserRole)
            settings_to_display = self.module_action.current_experiment.base_settings[selected_module].as_dict()
            for key, value in settings_to_display[str(selected_module)].items():
                self._create_tree_item(self.module_widget.baseSettingsTreeWidget, key, value)
        else:
            self.module_widget.baseSettingsTreeWidget.setEnabled(False)

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
                is_accepted = False

            if is_accepted:
                key_sequence = self._find_key_sequence(item, [])
                print(new_value)
                selected_module = self.module_widget.modulesIncludedListWidget.currentItem().data(QtCore.Qt.UserRole)
                parent_setting_object = self.module_action.current_experiment.base_settings[selected_module]

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
            return ExperimentManagerDialog._find_key_sequence(tree_item.parent(), key_list)

    @staticmethod
    def _create_tree_item(parent, key, value):
        if isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, key)

            for inner_key, inner_value in value.items():
                ExperimentManagerDialog._create_tree_item(item, inner_key, inner_value)
            return item
        if isinstance(value, list):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, key)

            for index, inner_value in enumerate(value):
                ExperimentManagerDialog._create_tree_item(item, index, inner_value)
            return item
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, key)
            item.setData(1, 0, value)
            return item
