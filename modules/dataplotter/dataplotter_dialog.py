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


class DataPlotterDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.DATA_PLOTTER, module_manager=module_manager, parent=parent)
        self._module_manager = module_manager
        # # set current data file name
        # self._module_widget.lbl_data_filename.setText("< none >")
        #
        # # set message text
        # self._module_widget.lbl_message_plotter.setText("not recording")
        # self._module_widget.lbl_message_plotter.setStyleSheet('color: orange')
        #
        # # get news items
        self.news = self.module_manager.news
        #
        # self._module_widget.browsePathPushButton.clicked.connect(self._browse_datalog_path)
        self.module_manager.state_machine.add_state_change_listener(self.handle_state_change)
        self.handle_state_change()

    def update_dialog(self):
        variables_to_plot = self.module_manager.module_settings.variables_to_be_plotted
        self._set_all_checked_items(variables_to_plot)

    def handle_state_change(self):
        pass

    def _save_settings(self):
        self.apply_settings()
        super()._save_settings()

    def apply_settings(self):
        self.module_manager.module_settings.variables_to_be_plotted = self._get_all_checked_items()

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
        By pretending that a click event has happened, Dataplotter settings will be written
        """
        self._module_widget.treeWidget.clear()

        for module in JOANModules:
            if module is not JOANModules.DATA_PLOTTER:
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
                DataPlotterDialog._create_tree_item(item, prop, None)

            for inner_key, inner_value in value.__dict__.items():
                if inner_key[0] != '_' and not callable(inner_value):
                    DataPlotterDialog._create_tree_item(item, inner_key, inner_value)
            return item
        elif isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for inner_key, inner_value in value.items():
                DataPlotterDialog._create_tree_item(item, inner_key, inner_value)
            return item
        elif isinstance(value, list):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for index, inner_value in enumerate(value):
                DataPlotterDialog._create_tree_item(item, str(index), inner_value)
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
