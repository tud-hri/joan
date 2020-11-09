import os
import inspect

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt

from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules

from core.news import News
from core.settings import Settings


class DatarecorderMPDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.DATARECORDER_MP, module_manager=module_manager, parent=parent)
        
        # set current data file name
        self._module_widget.lbl_data_filename.setText("< none >")

        # set current data directory name
        self._module_widget.lbl_data_directoryname.setText("TODO: filenameself.module_action.directoryname")

        # set message text
        self._module_widget.lbl_message_recorder.setText("not recording")
        self._module_widget.lbl_message_recorder.setStyleSheet('color: orange')

        # get news items
        self.news = News()

        # get settings
        self.settings = Settings()

        # Log files
        self.log_dir_menu = QtWidgets.QMenu('Log files')
        self.log_dir = QtWidgets.QAction('Select Directory')
        self.log_dir_menu.addAction(self.log_dir)
        self.menu_bar.addMenu(self.log_dir_menu)
        self.log_dir.triggered.connect(self._set_datalog_path)
        self.log_dir.setEnabled(True)
        self._module_widget.lbl_data_directoryname.mouseReleaseEvent = self._set_datalog_path

        # create tree widget
        #self.create_tree_widget()

    def _load_settings(self):
        """
        Opens dialog to load settings
        When loading is cancelled, the default settings are used, otherwise the loaded fiule is used
        State is set to READY
        """
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings',
                                                                         os.path.join(self.module_action.module_path,
                                                                                      'action'),
                                                                         filter='*.json')

        if settings_file_to_load:
            self.module_action.load_settings(settings_file_to_load)
            self.create_tree_widget()

    def _set_datalog_path(self, event):
        """
        Sets the path to datalog and let users create folders
        When selecting is cancelled, the previous path is used
        """

        file_path = QtWidgets.QFileDialog.getExistingDirectory(self, 
                                                               'select directory',
                                                               self.module_action.directoryname)

        if file_path:
            self.module_action.directoryname = file_path
            self._module_widget.lbl_data_directoryname.setText(self.module_action.directoryname)

    def _skip_event(self, event):
        pass

    def handle_click(self, nodes):
        """
        For each item a pedigree is built up starting at the item-level and working upwards 
        to the top-level, which is the module-key
        The handling of these items into the Datarecorder settings is done in the Action module
        :param nodes: contains a list of the deepest tree level items
        """
        for node in nodes:
            state = (node.checkState(0) > 0)
            node_path = []
            while node:
                node_path.append(node.text(0))
                node = node.parent()
            node_from_top = node_path[::-1]
            node_from_top.append(state)
        
        print("zie: DatarecorderMPDialog, TODO: handle self.module_action.handle_dialog_checkboxes(node_from_top)")
        #TODO: handle self.module_action.handle_dialog_checkboxes(node_from_top)

    def get_subtree_nodes(self, tree_widget_item):
        """
        Recursively take all QTreeWidgetItems in the subtree of the current tree_widget
        :param tree_widget_item: current tree widget item to take further action on
        :return: a list of deepest items
        """
        nodes = []
        nodes.append(tree_widget_item)

        if tree_widget_item.childCount() > 0:
            for i in range(tree_widget_item.childCount()):
                nodes.extend(self.get_subtree_nodes(tree_widget_item.child(i)))
        else:
            self.handle_click(nodes)
            write = 'No'
            if tree_widget_item.checkState(0) > 0:
                write = 'Yes'
            tree_widget_item.setData(1, Qt.DisplayRole, write)
        return nodes

    def get_all_items(self, tree_widget):
        """
        Returns all QTreeWidgetItems in the given QTreeWidget
        :param tree_widget: contains the tree widget items
        """
        all_items = []
        for i in range(tree_widget.topLevelItemCount()):
            top_item = tree_widget.topLevelItem(i)
            all_items.extend(self.get_subtree_nodes(top_item))
        return all_items

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def on_item_clicked(self):
        """
        A slot to pick up the click event signal on the treewidget item
        Every click somewhere on the tree widget starts a handle for all items
        :param: the selected tree widget item
        """
        self.get_all_items(self._module_widget.treeWidget)

    def create_tree_widget(self, _news):
        """
        Reads, or creates default settings when starting the module
        By pretending that a click event has happened, Datarecorder settings will be written
        """
        self._module_widget.treeWidget.clear()

        
        variables_to_save = {}
        for name, member in JOANModules.__members__.items():
            shared_variables = _news.read_news(member)
            variables_to_save[name] = shared_variables
            '''
            for variable in inspect.getmembers(shared_variables):
                try:
                    var_type = type(getattr(shared_variables, variable[0], None))
                    var = getattr(shared_variables, variable[0], None)
                    if not variable[0].startswith('_') and var_type in (int, str, float):
                        if not inspect.ismethod(variable[1]):
                            print('name: %s, value: %s, type: %s\n' % (variable[0], var, var_type))
                            variables_to_save[name] = var
                except AttributeError as inst:
                    print('Error', inst)

            '''
        #variables_to_save = self.module_action.settings.get_variables_to_save()
        CreateTreeWidgetDialog(variables_to_save, self._module_widget.treeWidget)
        self._module_widget.treeWidget.itemClicked.connect(self.on_item_clicked)
        self.on_item_clicked()


    def update_dialog(self):
        """
        Update the dialog based on a variable in the shared values
        :return:
        """
        if self._module_manager.shared_variables:
            pass
            #print('datarecorder: update_dialog state', str(self._module_manager.shared_variables.state))
            #self._module_widget.lbl_time.setText("State: " + str(self._module_manager.shared_variables.state))


class CreateTreeWidgetDialog(QtWidgets.QDialog):
    """
    Creates a recursive treewidget from the available news-items from all initialized modules
    except for the Data Recorder
    The dialog is shown and editable in the Data Recorder Settings part
    """

    def __init__(self, variable_to_save, tree_widget=None, parent=None):
        """
        :param variabele_to_save: contains all Data Recorder settings from the default_settings_file_location
        :param tree_widget: the tree which is built up
        :param parent:
        """
        super().__init__(parent)

        for module_key, module_news in variable_to_save.items():
            if module_news and module_key != str(JOANModules.DATARECORDER_MP):  # show only modules with shared_variables
                self._create_tree_item(tree_widget, module_key, module_news)
        self.show()

    @staticmethod
    def _create_tree_item(parent, key, value):
        """
        Tree-items are created here.
        :param parent: parent of the current key/value
        :param key: current used key
        :param value: current used value
        :return: the item within the tree
        """
        if isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            item.setFlags(item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for inner_key, inner_value in value.items():
                CreateTreeWidgetDialog._create_tree_item(item, inner_key, inner_value)
            return item
        if isinstance(value, list):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            for index, inner_value in enumerate(value):
                CreateTreeWidgetDialog._create_tree_item(item, str(index), inner_value)
            return item
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))
            if value:
                item.setCheckState(0, Qt.Checked)
                item.setData(1, Qt.DisplayRole, 'Yes')
            else:
                item.setCheckState(0, Qt.Unchecked)
                item.setData(1, Qt.DisplayRole, 'No')

            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            return item
