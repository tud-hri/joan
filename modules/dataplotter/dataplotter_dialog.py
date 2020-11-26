import pyqtgraph as pg
import numpy as np

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

        # # get news items
        self.news = self.module_manager.news

        self.module_manager.state_machine.add_state_change_listener(self.handle_state_change)
        self.handle_state_change()

        background_color = pg.mkColor((240, 240, 240, 255))

        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'k')

        self._module_widget.plot_graph.setBackground(background_color)
        viewbox = self._module_widget.plot_graph.getViewBox()
        viewbox.setBorder(pen=pg.mkPen(0, 0, 0, 255))
        viewbox.setBackgroundColor((255, 255, 255, 200))
        self._module_widget.plot_graph.showGrid(True, True, 1)

        self.plot_handles = {}
        self.ydata_listdict = {}
        self.time_list = [-5 + x * (0 - -5) / 50 for x in range(50)]
        self.pencolor_dict = {}

        self.data_container = [[0]*1000]*50
        # print(self.data_container)



    def initialize_dialog(self):
        self.variables_to_plot = self.module_manager.module_settings.variables_to_be_plotted
        self._set_all_checked_items(self.variables_to_plot)

    def update_dialog(self):
        variables_to_plot = self._get_all_checked_items()
        variables_to_clear = self._get_all_unchecked_items()

        if len(variables_to_plot) == 0:
            for plots in self.plot_handles.values():
                plots.setData(x =[0], y=[0])

        for variable in variables_to_clear:
                plot_handle_key = '.'.join(variable)
                all_plot_handle_keys = self.plot_handles.keys()
                for string_keys in all_plot_handle_keys:
                    if plot_handle_key in string_keys:
                        self.plot_handles[string_keys].setData(x = [0], y =[0])

        for variable in variables_to_plot:
            module = JOANModules.from_string_representation(variable[0])
            last_object = self.news.read_news(module)

            for attribute_name in variable[1:]:
                if isinstance(last_object, dict):
                    last_object = last_object[attribute_name]
                elif isinstance(last_object, list):
                    last_object = last_object[int(attribute_name)]
                else:
                    last_object = getattr(last_object, attribute_name)

                if isinstance(last_object, list):
                    for strings in self.plot_handles.keys():
                        variable_name = strings.rsplit('.')
                        if attribute_name == variable_name[-2] and variable[0] == variable_name[0]:
                                self.ydata_listdict[strings].append(float(last_object[int(variable_name[-1])]))
                                self.ydata_listdict[strings].pop(0)

                        self.plot_handles[strings].setData(x=self.time_list, y=self.ydata_listdict[strings])

                elif isinstance(last_object, float or int or bool):
                    for strings in self.plot_handles.keys():
                        variable_name = strings.rsplit('.')
                        if attribute_name == variable_name[-1] and variable[0] == variable_name[0]:
                            self.ydata_listdict[strings].append(float(last_object))
                            self.ydata_listdict[strings].pop(0)
                            self.plot_handles[strings].setData(x = self.time_list, y = self.ydata_listdict[strings])

    def handle_state_change(self):
        if self.module_manager.state_machine.current_state == State.INITIALIZED:
            self._module_widget.treeWidget.setEnabled(False)
            self._fill_tree_widget()
            self.initialize_dialog()
        elif self.module_manager.state_machine.current_state == State.STOPPED:
            self._module_widget.treeWidget.setEnabled(False)
            try:
                for plots in self.plot_handles.values():
                    plots.setData(x =[0], y=[0])
                    plots.clear()
            except AttributeError: #this means there are no plots yet
                pass
        else:
            self._module_widget.treeWidget.setEnabled(True)

    def _save_settings(self):
        self.apply_settings()
        super()._save_settings()

    def apply_settings(self):
        self._check_all_items(self._module_widget.treeWidget.invisibleRootItem())
        self.module_manager.module_settings.variables_to_be_plotted = self._get_all_checked_items()
        for variables in self.module_manager.module_settings.variables_to_be_plotted:
            module = JOANModules.from_string_representation(variables[0])
            last_object = self.news.read_news(module)

            for attribute_name in variables[1:]:
                if isinstance(last_object, dict):
                    last_object = last_object[attribute_name]
                elif isinstance(last_object, list):
                    last_object = last_object[int(attribute_name)]
                else:
                    last_object = getattr(last_object, attribute_name)

                if isinstance(last_object, float or int or bool):
                    self.ydata_listdict['.'.join(variables)]= [0]*50
                    self.ydata_listdict['.'.join(variables)] = [0] * 50
                    color = list(np.random.choice(range(256), size=3))
                    self.plot_handles['.'.join(variables)] = self._module_widget.plot_graph.plot(x=[0], y=[0], size=2,
                                                                                                 pen=pg.mkPen((color[0], color[1], color[2], 255), width=3))
                elif isinstance(last_object, list):
                    for idx, value in enumerate(last_object):
                        variables.append(str(idx))
                        self.ydata_listdict['.'.join(variables)]= [0]*50
                        color = list(np.random.choice(range(256), size=3))
                        self.plot_handles['.'.join(variables)] = self._module_widget.plot_graph.plot(x=[0], y=[0], size=2,
                                                                                                     pen=pg.mkPen((color[0], color[1], color[2], 255), width=3))
                        variables.remove(str(idx))


        self._uncheck_all_items(self._module_widget.treeWidget.invisibleRootItem())



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

    def _get_all_unchecked_items(self):
        unchecked_items = []
        self._recursively_get_unchecked_items(self._module_widget.treeWidget.invisibleRootItem(), [] , unchecked_items)
        return unchecked_items

    def _check_all_items(self, parent):
        for index in range(parent.childCount()):
            child = parent.child(index)
            child.setCheckState(0, QtCore.Qt.Checked)

    def _uncheck_all_items(self, parent):
        for index in range(parent.childCount()):
            child = parent.child(index)
            child.setCheckState(0, QtCore.Qt.Unchecked)

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

    def _recursively_get_unchecked_items(self, parent, path_to_parent, list_of_unchecked_items):
        for index in range(parent.childCount()):
            child = parent.child(index)

            new_list = path_to_parent.copy()
            new_list.append(child.text(0))

            if not child.childCount():
                if child.checkState(0) == QtCore.Qt.Unchecked:
                    list_of_unchecked_items.append(new_list)

            else:
                self._recursively_get_unchecked_items(child, new_list, list_of_unchecked_items)

    def _fill_tree_widget(self):
        """
        Reads, or creates default settings when starting the module
        By pretending that a click event has happened, Dataplotter settings will be written
        """
        self._module_widget.treeWidget.clear()

        for module in JOANModules:
            if module is not JOANModules.DATA_PLOTTER:
                shared_variables = self.news.read_news(module)
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
