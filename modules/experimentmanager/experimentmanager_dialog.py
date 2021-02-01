import os

from PyQt5 import QtWidgets, QtCore, QtGui

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from core.statesenum import State
from modules.experimentmanager.condition import Condition
from modules.experimentmanager.editexperimentdialog import EditExperimentDialog
from modules.joanmodules import JOANModules
from .newexperimentdialog import NewExperimentDialog


class ExperimentManagerDialog(ModuleDialog):
    module_manager: ModuleManager

    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, module_manager=module_manager, parent=parent)
        self.module_widget.autoTransitionCheckBox.setChecked(True)
        self.module_widget.btn_create_experiment.clicked.connect(self.create_new_experiment)
        self.module_widget.btn_load_experiment.clicked.connect(self.load_experiment)
        self.module_widget.btn_edit_experiment.clicked.connect(self.open_experiment_dialog)
        self.module_widget.btn_edit_experiment.setEnabled(False)
        self.module_widget.autoTransitionCheckBox.toggled.connect(self._update_enabled_buttons)

        self.module_manager.central_state_monitor.add_combined_state_change_listener(self.update_gui)
        self.module_manager.central_state_monitor.add_combined_state_change_listener(self._check_auto_transition)

        self.module_widget.btn_create_experiment.setToolTip("Create a new experiment with the current settings as base settings.")
        self.module_widget.btn_load_experiment.setToolTip("Load an experiment from a JSON file.")
        self.module_widget.btn_edit_experiment.setToolTip("Edit the current experiment.")

        self.module_widget.btn_activate_condition.clicked.connect(self.activate_selected_condition)
        self.module_widget.condition_list.currentItemChanged.connect(self._update_enabled_buttons)
        self.module_widget.btn_transition_to_next.clicked.connect(self.transition_to_next_condition)

        self.experiment_dialog = None

        # get rid of the settings menu - we don't need it here
        self.settings_menu.clear()
        self.settings_menu = None

    def create_new_experiment(self):
        new_experiment_dialog = NewExperimentDialog(self.module_manager.singleton_settings.all_settings_keys, parent=self)
        new_experiment_dialog.accepted.connect(
            lambda: self.module_manager.create_new_experiment(new_experiment_dialog.modules_to_include, new_experiment_dialog.file_path))

    def load_experiment(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Experiment', './experiments', filter='JSON (*.json)')
        if file_path:
            self.module_manager.load_experiment(file_path)

    def _check_auto_transition(self):
        """
        An action that is called when the central state machine transitions. It checks if the central state is stopped and then auto transitions when needed.
        :return:
        """
        if self.module_manager.central_state_monitor.combined_state is State.STOPPED and self.module_widget.autoTransitionCheckBox.isChecked():
            self.transition_to_next_condition()

    def _update_enabled_buttons(self):
        if self.module_manager.central_state_monitor.combined_state is State.INITIALIZED:
            self.module_widget.btn_edit_experiment.setEnabled(bool(self.module_manager.current_experiment))
            self.module_widget.btn_create_experiment.setEnabled(True)
            self.module_widget.btn_load_experiment.setEnabled(True)
            self.module_widget.btn_activate_condition.setEnabled(False)
            self.module_widget.btn_transition_to_next.setEnabled(False)

        elif self.module_manager.central_state_monitor.combined_state is State.STOPPED:
            self.module_widget.btn_load_experiment.setEnabled(True)
            self.module_widget.btn_edit_experiment.setEnabled(False)
            self.module_widget.btn_create_experiment.setEnabled(False)

            if self.module_manager.current_experiment:
                if bool(self.module_widget.condition_list.currentItem()):
                    selected_current_is_condition = isinstance(self.module_widget.condition_list.currentItem().data(QtCore.Qt.UserRole), Condition)
                else:
                    selected_current_is_condition = False
                self.module_widget.btn_activate_condition.setEnabled(selected_current_is_condition)
                self.module_widget.btn_transition_to_next.setEnabled(len(
                    self.module_manager.current_experiment.active_condition_sequence) and self.module_manager.active_condition_index != len(
                    self.module_manager.current_experiment.active_condition_sequence) - 1)
            else:
                self.module_widget.btn_activate_condition.setEnabled(False)
                self.module_widget.btn_transition_to_next.setEnabled(False)
        else:
            self.module_widget.btn_edit_experiment.setEnabled(False)
            self.module_widget.btn_create_experiment.setEnabled(False)
            self.module_widget.btn_load_experiment.setEnabled(False)
            self.module_widget.btn_activate_condition.setEnabled(False)
            self.module_widget.btn_transition_to_next.setEnabled(False)

    def update_gui(self):
        self.update_condition_lists()
        self._update_enabled_buttons()

        if self.module_manager.current_experiment:
            self.module_widget.lbl_loaded_experiment.setText(os.path.abspath(self.module_manager.experiment_save_path).split('\\')[-1])
        else:
            self.module_widget.lbl_loaded_experiment.setText('-')

    def update_condition_lists(self):
        """
        updates the display of available conditions and transitions.
        :return:
        """
        self.module_widget.condition_list.clear()

        if self.module_manager.current_experiment:
            self.module_widget.condition_list.setEnabled(True)

            for condition_or_transition in self.module_manager.current_experiment.active_condition_sequence:
                item = QtWidgets.QListWidgetItem(condition_or_transition.name)
                item.setData(QtCore.Qt.UserRole, condition_or_transition)
                if not isinstance(condition_or_transition, Condition):
                    item.setBackground(QtGui.QBrush(QtGui.QColor(200, 100, 200, 50)))
                self.module_widget.condition_list.addItem(item)
        else:
            self.module_widget.condition_list.setEnabled(False)

        self._update_enabled_buttons()
        self._update_highlighted_condition()

    def activate_selected_condition(self):
        current_selected_condition = self.module_widget.condition_list.currentItem().data(QtCore.Qt.UserRole)
        success = self.module_manager.activate_selected_condition(current_selected_condition, self.module_widget.condition_list.currentRow())

        if success:
            self._update_highlighted_condition()
            self._update_enabled_buttons()

    def transition_to_next_condition(self):
        success = self.module_manager.transition_to_next_condition()
        if success:
            self._update_highlighted_condition()
            self._update_enabled_buttons()

    def open_experiment_dialog(self):
        """
        Create and open an experiment dialog
        Note: this dialog is always "freshly" created, and the experiment is then loaded in
        :return:
        """
        self.experiment_dialog = EditExperimentDialog(self.module_manager.current_experiment, self.module_manager.experiment_save_path,
                                                      self.module_manager.singleton_settings, parent=self)
        self.module_widget.btn_edit_experiment.blockSignals(True)
        self.module_widget.btn_edit_experiment.setEnabled(False)

        self.experiment_dialog.accepted.connect(self.update_condition_lists)
        self.experiment_dialog.finished.connect(lambda: self.module_widget.btn_edit_experiment.blockSignals(False))
        self.experiment_dialog.finished.connect(lambda: self.module_widget.btn_edit_experiment.setEnabled(True))

    def _update_highlighted_condition(self):
        if self.module_manager.current_experiment and self.module_manager.active_condition:
            for item_index in range(self.module_widget.condition_list.count()):
                item = self.module_widget.condition_list.item(item_index)
                if item.data(QtCore.Qt.UserRole) is self.module_manager.active_condition and item_index == self.module_manager.active_condition_index:
                    item.setBackground(QtGui.QBrush(QtGui.QColor(50, 255, 50, 100)))
                elif not isinstance(item.data(QtCore.Qt.UserRole), Condition):
                    item.setBackground(QtGui.QBrush(QtGui.QColor(200, 100, 200, 50)))
                else:
                    item.setBackground(QtGui.QBrush(QtCore.Qt.NoBrush))
