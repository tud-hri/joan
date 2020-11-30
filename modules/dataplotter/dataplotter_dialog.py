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
        self.viewbox = self._module_widget.plot_graph.getViewBox()
        self.viewbox.setBorder(pen=pg.mkPen(0, 0, 0, 255))
        self.viewbox.setBackgroundColor((255, 255, 255, 200))
        self._module_widget.plot_graph.showGrid(True, True, 1)

        self.plot_handle_dict = {}
        self.ydata_listdict = {}
        self.empty_y = [0] * 50
        self.time_list = [-5 + x * (0 - -5) / 50 for x in range(50)]
        self.pencolor_dict = {}

        self.data_container = [[0] * 1000] * 50

        self._module_widget.treeWidget.itemChanged.connect(self.handleItemChanged)

    def initialize_dialog(self):
        self.variables_to_plot = self.module_manager.module_settings.variables_to_be_plotted
        self._set_all_checked_items(self.variables_to_plot)
        self.overall_legend = pg.LegendItem(offset=10, horSpacing=30, verSpacing=-7,
                                      pen=pg.mkPen(0, 0, 0, 255), brush=pg.mkBrush(255, 255, 255, 255))
        self.overall_legend.setParentItem(self.viewbox)
        self._module_widget.plot_graph.setLabel('bottom', 'Time[s]', **{'font-size': '12pt'})



    def handleItemChanged(self, item, column):
        if (self.module_manager.state_machine.current_state is not State.INITIALIZED) and (self.module_manager.state_machine.current_state is not State.STOPPED):
            item_variable_path_list = self._get_item_path(item)
            item_variable_path_list.reverse()
            if item.checkState(column) == Qt.Checked:
                color = list(np.random.choice(range(256), size=3))
                self.plot_handle_dict['.'.join(item_variable_path_list)] = pg.PlotDataItem(name='.'.join(item_variable_path_list), x=self.time_list, y=self.empty_y, size=2,
                                                                                           pen=pg.mkPen((color[0], color[1], color[2], 255), width=3))
                self._module_widget.plot_graph.addItem(self.plot_handle_dict['.'.join(item_variable_path_list)])
                self.ydata_listdict['.'.join(item_variable_path_list)] = [0] * 50
                self.overall_legend.addItem(self.plot_handle_dict['.'.join(item_variable_path_list)], item_variable_path_list[-1])

            elif item.checkState(column) == Qt.Unchecked:
                self.ydata_listdict['.'.join(item_variable_path_list)] = [0] * 50
                self.plot_handle_dict['.'.join(item_variable_path_list)].clear()
                self._module_widget.plot_graph.removeItem(self.plot_handle_dict['.'.join(item_variable_path_list)])
                self.overall_legend.removeItem(self.plot_handle_dict['.'.join(item_variable_path_list)])
                del self.plot_handle_dict['.'.join(item_variable_path_list)]

    def _get_item_path(self, item):
        temp = [item.text(0)]
        path = self._recursively_get_item_path(item, temp)
        return path

    def _recursively_get_item_path(self, child, path):
        parent = child.parent()
        if parent is not None:
            new_list = path.copy()
            new_list.append(parent.text(0))
            return self._recursively_get_item_path(parent, new_list)
        else:
            return path

    def update_dialog(self):
        variables_to_plot = self._get_all_checked_items()
        for variable in variables_to_plot:
            module = JOANModules.from_string_representation(variable[0])
            last_object = self.news.read_news(module)

            for attribute_name in variable[1:]:
                if isinstance(last_object, dict):
                    last_object = last_object[attribute_name]
                elif isinstance(last_object, list):
                    for strings in self.plot_handle_dict.keys():
                        variable_name = strings.rsplit('.')
                        variable_index = self.convert_variablename_to_index(variable_name[-1])
                        if attribute_name == variable_name[-1] and variable[-2] == variable_name[-2] and variable_name[-3] == variable[-3]:
                            self.ydata_listdict[strings].append(float(last_object[variable_index]))
                            self.ydata_listdict[strings].pop(0)
                else:
                    last_object = getattr(last_object, attribute_name)
                    for strings in self.plot_handle_dict.keys():
                        variable_name = strings.rsplit('.')
                        if attribute_name == variable_name[-1] and variable[-2] == variable_name[-2]:
                            self.ydata_listdict[strings].append(float(last_object))
                            self.ydata_listdict[strings].pop(0)

        for plot_item in self.plot_handle_dict.values():
            plot_item.setData(x=self.time_list, y=self.ydata_listdict[plot_item.name()])

    def handle_state_change(self):
        if self.module_manager.state_machine.current_state == State.INITIALIZED:
            self._module_widget.treeWidget.setEnabled(True)
            self.initialize_dialog()
        elif self.module_manager.state_machine.current_state == State.STOPPED:
            self._module_widget.treeWidget.clear()
            self._module_widget.plot_graph.clear()
            try:
                self.overall_legend.scene().removeItem(self.overall_legend)
            except AttributeError:
                pass
        else:
            self._module_widget.treeWidget.setEnabled(True)

    def _save_settings(self):
        self.apply_settings()
        super()._save_settings()

    def apply_settings(self):
        self._fill_tree_widget()

    def _set_all_checked_items(self, variables_to_plot):
        self._recursively_set_checked_items(self._module_widget.treeWidget.invisibleRootItem(), [], variables_to_plot)

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
        self._recursively_get_unchecked_items(self._module_widget.treeWidget.invisibleRootItem(), [], unchecked_items)
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

    def _recursively_get_all_items(self, parent, path_to_parent, list_of_items):
        for index in range(parent.childCount()):
            child = parent.child(index)

            new_list = path_to_parent.copy()
            new_list.append(child.text(0))

            if not child.childCount():
                list_of_items.append(new_list)

            else:
                self._recursively_get_all_items(child, new_list, list_of_items)

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

    def _create_tree_item(self, parent, key, value):
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

            for prop in value.get_all_properties():
                if prop is not None:
                    last_object = getattr(value, prop)
                    DataPlotterDialog._create_tree_item(self, item, prop, last_object)

            for inner_key, inner_value in value.__dict__.items():
                if inner_key[0] != '_' and not callable(inner_value):
                    DataPlotterDialog._create_tree_item(self, item, inner_key, inner_value)
            return item
        elif isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            for inner_key, inner_value in value.items():
                DataPlotterDialog._create_tree_item(self, item, inner_key, inner_value)
            return item
        elif isinstance(value, list):
            if 'data_road' not in str(key):
                item = QtWidgets.QTreeWidgetItem(parent)
                item.setData(0, Qt.DisplayRole, str(key))
                print(item.text(0))
                for index, inner_value in enumerate(value):
                    # Hardcoded formatting of strings for mostly used variables:
                    variable_name = self.convert_indexes_to_variable_names(item.text(0), index)

                    DataPlotterDialog._create_tree_item(self, item, variable_name, inner_value)
                return item
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            item.setCheckState(0, Qt.Unchecked)

            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            return item


    def convert_indexes_to_variable_names(self, list_name, index):
        if list_name == 'accelerations':
            if index == 0:
                return 'X Acceleration'
            elif index == 1:
                return 'Y Acceleration'
            elif index == 2:
                return 'Z Acceleration'

        elif list_name == 'transform':
            if index == 0:
                return 'X Position'
            elif index == 1:
                return 'Y Position'
            elif index == 2:
                return 'Z Position'
            elif index == 3:
                return 'Yaw'
            elif index == 4:
                return 'Pitch'
            elif index == 5:
                return 'Roll'

        elif list_name == 'velocities':
            if index == 0:
                return 'X Velocity'
            elif index == 1:
                return 'Y Velocity'
            elif index == 2:
                return 'Z Velocity'
            elif index == 3:
                return 'Angular Velocity X'
            elif index == 4:
                return 'Angular Velocity Y'
            elif index == 5:
                return 'Angular Velocity Z'

        elif list_name == 'applied_input':
            if index == 0:
                return 'Steering'
            elif index == 1:
                return 'Reverse'
            elif index == 2:
                return 'Handbrake'
            elif index == 3:
                return 'Brake'
            elif index == 4:
                return 'Throttle'

        else:
            return str(index)

    def convert_variablename_to_index(self, variable_name):

        if variable_name == 'X Acceleration':
            return 0
        elif variable_name == 'Y Acceleration':
            return 1
        elif variable_name == 'Z Acceleration':
            return 2

        elif variable_name == 'X Position':
            return 0
        elif variable_name == 'Y Position':
            return 1
        elif variable_name == 'Z Position':
            return 2

        elif variable_name == 'Yaw':
            return 3
        elif variable_name == 'Pitch':
            return 4
        elif variable_name == 'Roll':
            return 5

        elif variable_name == 'X Velocity':
            return 0
        elif variable_name == 'X Velocity':
            return 1
        elif variable_name == 'X Velocity':
            return 2
        elif variable_name == 'Angular Velocity X':
            return 3
        elif variable_name == 'Angular Velocity Y':
            return 4
        elif variable_name == 'Angular Velocity Z':
            return 5

        elif variable_name == 'Steering':
            return 0
        elif variable_name == 'Reverse':
            return 1
        elif variable_name == 'Handbrake':
            return 2
        elif variable_name == 'Brake':
            return 3
        elif variable_name == 'Throttle':
            return 4

        else:
            return 0