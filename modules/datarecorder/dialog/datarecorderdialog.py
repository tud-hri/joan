import os
import glob
import numpy as np

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt

from modules.joanmodules import JOANModules
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State
from process import News

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
            if module_news and module_key != str(JOANModules.DATA_RECORDER):  # show only modules with news
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

class DatarecorderDialog(JoanModuleDialog):
    """
    Builts the dialog used for the Data Recorder and shows it on the inherited dialog
    Inherits the dialog from the JoanModuleDialog
    """
    def __init__(self, module_action: JoanModuleAction, parent=None):
        """
        :param module_action: contains the Datarecorder Action class
        :param parent:
        """
        super().__init__(module=JOANModules.DATA_RECORDER, module_action=module_action, parent=parent)

        self.module_action.state_machine.add_state_change_listener(self._handle_module_specific_state)
        self.module_action.state_machine.set_entry_action(State.READY, self.create_tree_widget)

        # set current data file name
        self.module_widget.lbl_data_filename.setText("< none >")

        # set message text
        self.module_widget.lbl_message_recorder.setText("not recording")
        self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')

        # get news items
        self.news = News()

        # Settings
        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Datarecorder Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Datarecorder Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)
        # load/save file
        self.load_settings.setEnabled(True)
        self.save_settings.setEnabled(False)

        # set trajectory buttons functionality
        self.module_widget.btn_save.setEnabled(False)
        self.module_widget.btn_discard.setEnabled(False)
        self.module_widget.line_trajectory_title.setEnabled(False)
        self.module_widget.check_trajectory.setEnabled(False)
        self.module_widget.btn_save.clicked.connect(self.save_trajectory)
        self.module_widget.btn_discard.clicked.connect(self.discard_trajectory)
        self.module_widget.check_trajectory.stateChanged.connect(self.check_trajectory_checkbox)
        self.module_widget.line_trajectory_title.textEdited.connect(self.check_trajectory_filename)

    def _load_settings(self):
        """
        Opens dialog to load settings
        When loading is cancelled, the default settings are used, otherwise the loaded fiule is used
        State is set to READY
        """
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings', filter='*.json')
        if settings_file_to_load:
            self.module_action.load_settings_from_file(settings_file_to_load)
            self.create_tree_widget()
        self.module_action.state_machine.request_state_change(State.READY)

    def _save_settings(self):
        """
        Opens a dialog to save the current settings in a json formatted file with the json extension
        """
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings', filter='*.json')
        if file_to_save_in:
            self.module_action.save_settings_to_file(file_to_save_in)


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
        self.module_action.handle_dialog_checkboxes(node_from_top)

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
        self.get_all_items(self.module_widget.treeWidget)

    def create_tree_widget(self):
        """
        Reads, or creates default settings when starting the module
        By pretending that a click event has happened, Datarecorder settings will be written
        """
        self.module_widget.treeWidget.clear()
        variables_to_save = self.module_action.settings.get_variables_to_save()
        CreateTreeWidgetDialog(variables_to_save, self.module_widget.treeWidget)
        self.module_widget.treeWidget.itemClicked.connect(self.on_item_clicked)
        self.on_item_clicked()

    def check_trajectory_checkbox(self):
        self.module_action.trajectory_recorder.trajectory_record_boolean(self.module_widget.check_trajectory.isChecked())

    def check_trajectory_filename(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        hcr_path = os.path.join(path,'steeringwheelcontrol/action/swcontrollers/trajectories/*.csv')  #Dit moet handiger kunnen

        self.trajectory_title = self.module_widget.line_trajectory_title.text()

        for fname in glob.glob(hcr_path):
            if (self.trajectory_title == (os.path.basename(fname)[:-4]) or self.trajectory_title == ''):
                self.module_widget.label_trajectory_filename.setText('Filename Invalid! (empty or already exists)')
                self.module_widget.btn_save.setEnabled(False)
                break
            else:
                self.module_widget.btn_save.setEnabled(True)
                self.module_widget.label_trajectory_filename.setText('Will save file as: '+ self.trajectory_title + '.csv')

    def save_trajectory(self):
        self.trajectory_data = self.module_action.trajectory_recorder.generate_trajectory()
        self.trajectory_data_visual = self.trajectory_data[0:len(self.trajectory_data):5]
        curpath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.dirname(os.path.dirname(curpath))
        hcr_path = os.path.join(path,'steeringwheelcontrol/action/swcontrollers/trajectories/')  #Dit moet handiger kunnen

        # Save 2D numpy array to csv file
        try:
            np.savetxt(hcr_path + self.trajectory_title + '.csv', self.trajectory_data, delimiter=',', fmt='%i, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f , %1.8f')
            np.savetxt(hcr_path + self.trajectory_title + '_VISUAL.csv', self.trajectory_data_visual, delimiter=',', fmt='%i, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f, %1.8f', header="Row Name,PosX,PosY,SteeringAngle,Throttle,Brake,Psi, Vel", comments='')
            self.module_widget.label_trajectory_filename.setText('Saved file as: '+ self.trajectory_title + '.csv')
            self.module_widget.line_trajectory_title.clear()
            self.module_widget.btn_save.setEnabled(False)
            self.module_widget.btn_discard.setEnabled(False)
            self.module_widget.line_trajectory_title.setEnabled(False)
            self.module_widget.check_trajectory.setEnabled(False)
            self.module_widget.check_trajectory.setChecked(False)
        except Exception as inst:
            print(inst)
            self.module_widget.label_trajectory_filename.setText('Could not save File please try again')
            self.module_widget.btn_save.setEnabled(True)
            self.module_widget.btn_discard.setEnabled(True)
            self.module_widget.line_trajectory_title.setEnabled(True)
            self.module_widget.check_trajectory.setEnabled(True)
            self.module_widget.check_trajectory.setChecked(True)

    def discard_trajectory(self):
        self.module_action.trajectory_recorder.discard_current_trajectory()
        self.module_widget.label_trajectory_filename.setText('Discarded trajectory')
        self.module_widget.line_trajectory_title.clear()
        self.module_widget.btn_save.setEnabled(False)
        self.module_widget.btn_discard.setEnabled(False)
        self.module_widget.line_trajectory_title.setEnabled(False)
        self.module_widget.check_trajectory.setEnabled(False)
        self.module_widget.check_trajectory.setChecked(False)

    def _handle_module_specific_state(self):
        """
        Handle the state transition by updating the status label and have the
        GUI reflect the possibilities of the current state.
        """
        try:
            current_state = self.module_action.state_machine.current_state

            if current_state is State.READY:
                self.state_widget.btn_start.setEnabled(True)
                self.state_widget.btn_stop.setEnabled(True)
                self.module_widget.check_trajectory.setEnabled(True)
                self.module_widget.lbl_data_filename.setText(self.module_action.get_filename())
                self.module_widget.label_trajectory_filename.setText('')
                if self.module_widget.check_trajectory.isChecked() is False:
                    self.module_widget.btn_save.setEnabled(False)
                    self.module_widget.btn_discard.setEnabled(False)
                    self.module_widget.line_trajectory_title.setEnabled(False)
                # set message text
                self.module_widget.lbl_message_recorder.setText("not recording")
                self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')
                # load/save file
                self.load_settings.setEnabled(False)
                self.save_settings.setEnabled(True)
                self.state_widget.input_tick_millis.setEnabled(False)
                self.state_widget.input_tick_millis.setStyleSheet("color: black;  background-color: lightgrey")

            if current_state is State.IDLE:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)

                self.module_widget.check_trajectory.setEnabled(False)
                self.module_widget.btn_save.setEnabled(False)
                self.module_widget.btn_discard.setEnabled(False)
                self.module_widget.line_trajectory_title.setEnabled(False)

                if self.module_widget.check_trajectory.isChecked():
                    self.module_widget.btn_save.setEnabled(True)
                    self.module_widget.btn_discard.setEnabled(True)
                    self.module_widget.line_trajectory_title.setEnabled(True)
                    self.check_trajectory_filename()
                # set message text
                self.module_widget.lbl_message_recorder.setText("not recording")
                self.module_widget.lbl_message_recorder.setStyleSheet('color: orange')
                # load/save file
                self.load_settings.setEnabled(True)
                self.save_settings.setEnabled(False)
                self.state_widget.input_tick_millis.setEnabled(True)
                self.state_widget.input_tick_millis.setStyleSheet("color: black;  background-color: white")

            if current_state is State.RUNNING:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(True)
                self.module_widget.check_trajectory.setEnabled(False)
                self.module_widget.btn_save.setEnabled(False)
                self.module_widget.btn_discard.setEnabled(False)
                self.module_widget.line_trajectory_title.setEnabled(False)
                # set message text
                self.module_widget.lbl_message_recorder.setText("Busy Recording ...")
                self.module_widget.lbl_message_recorder.setStyleSheet('color: red')
                # load/save file
                self.load_settings.setEnabled(False)
                self.save_settings.setEnabled(True)
                self.state_widget.input_tick_millis.setEnabled(False)
                self.state_widget.input_tick_millis.setStyleSheet("color: black;  background-color: lightgrey")

            # update the state label
            self.state_widget.lbl_module_state.setText(current_state.__str__())
            self.module_widget.repaint()

        except Exception as inst:
            print(inst)
