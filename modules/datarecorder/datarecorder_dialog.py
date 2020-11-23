import datetime
import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from core.sharedvariables import SharedVariables
from core.statesenum import State
from modules.joanmodules import JOANModules


class DataRecorderDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.DATA_RECORDER, module_manager=module_manager, parent=parent)
        self._module_manager = module_manager
        # set current data file name
        self._module_widget.lbl_data_filename.setText("< none >")

        # set message text
        self._module_widget.lbl_message_recorder.setText("not recording")
        self._module_widget.lbl_message_recorder.setStyleSheet('color: orange')

        # get news items
        self.news = self.module_manager.news

        self._module_widget.browsePathPushButton.clicked.connect(self._browse_datalog_path)
        self.module_manager.state_machine.add_state_change_listener(self.handle_state_change)
        self.handle_state_change()

    def update_dialog(self):
        file_path = self.module_manager.module_settings.path_to_save_file
        self._module_widget.lbl_data_filename.setText(os.path.basename(file_path))
        self._module_widget.lbl_data_directoryname.setText(os.path.dirname(file_path))

        variables_to_save = self.module_manager.module_settings.variables_to_be_saved
        self._set_all_checked_items(variables_to_save)

    def _browse_datalog_path(self):
        """
        Sets the path to datalog and let users create folders
        When selecting is cancelled, the previous path is used
        """
        date_string = datetime.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'select save destination', date_string, filter='*.csv')

        if file_path:
            self._module_widget.lbl_data_filename.setText(os.path.basename(file_path))
            self._module_widget.lbl_data_directoryname.setText(os.path.dirname(file_path))
            self.module_manager.module_settings.path_to_save_file = os.path.normpath(file_path)

    def handle_state_change(self):
        if self.module_manager.state_machine.current_state == State.INITIALIZED:
            self._module_widget.treeWidget.setEnabled(True)
            self._module_widget.browsePathPushButton.setEnabled(True)
            self._fill_tree_widget()
            self.update_dialog()
        elif self.module_manager.state_machine.current_state == State.STOPPED:
            self._module_widget.browsePathPushButton.setEnabled(True)
            self._module_widget.treeWidget.setEnabled(False)
        else:
            self._module_widget.browsePathPushButton.setEnabled(False)
            self._module_widget.treeWidget.setEnabled(False)

    def _save_settings(self):
        self.apply_settings()
        super()._save_settings()

    def apply_settings(self):
        self.module_manager.module_settings.variables_to_be_saved = self._get_all_checked_items()

    def _set_all_checked_items(self, variables_to_save):
        self._recursively_set_checked_items(self._module_widget.treeWidget.invisibleRootItem(), [], variables_to_save)

    def _recursively_set_checked_items(self, parent, path_to_parent, list_of_checked_items):
        for index in range(parent.childCount()):
            child = parent.child(index)

            new_list = path_to_parent.copy()
            new_list.append(child.text(0))

            if not child.childCount():
                if new_list in list_of_checked_items:
                    child.setCheckState(0, Qt.Checked)
                else:
                    child.setCheckState(0, Qt.Unchecked)
            else:
                self._recursively_set_checked_items(child, new_list, list_of_checked_items)

    def _get_all_checked_items(self):
        checked_items = []
        self._recursively_get_checked_items(self._module_widget.treeWidget.invisibleRootItem(), [], checked_items)
        return checked_items

    def _recursively_get_checked_items(self, parent, path_to_parent, list_of_checked_items):
        for index in range(parent.childCount()):
            child = parent.child(index)

            new_list = path_to_parent.copy()
            new_list.append(child.text(0))

            if not child.childCount():
                if child.checkState(0) == QtCore.Qt.Checked:
                    list_of_checked_items.append(new_list)
            else:
                self._recursively_get_checked_items(child, new_list, list_of_checked_items)

    def _fill_tree_widget(self):
        """
        Reads, or creates default settings when starting the module
        By pretending that a click event has happened, Datarecorder settings will be written
        """
        self._module_widget.treeWidget.clear()

        for module in JOANModules:
            if module is not JOANModules.DATA_RECORDER:
                shared_variables = self.news.read_news(module)
                print(shared_variables)
                if shared_variables:
                    self._create_tree_item(self._module_widget.treeWidget, str(module), shared_variables)

    @staticmethod
    def _create_tree_item(parent, key, value):
        """
        Tree-items are created here.
        :param parent: parent of the current key/value
        :param key: current used key
        :param value: current used value
        :return: the item within the tree
        """
        if isinstance(value, SharedVariables):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for prop in value.get_all_properties():
                DataRecorderDialog._create_tree_item(item, prop, None)

            for inner_key, inner_value in value.__dict__.items():
                if inner_key[0] != '_' and not callable(inner_value):
                    DataRecorderDialog._create_tree_item(item, inner_key, inner_value)
            return item
        elif isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for inner_key, inner_value in value.items():
                DataRecorderDialog._create_tree_item(item, inner_key, inner_value)
            return item
        elif isinstance(value, list):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for index, inner_value in enumerate(value):
                DataRecorderDialog._create_tree_item(item, str(index), inner_value)
            return item
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            if value:
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)

            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            return item
