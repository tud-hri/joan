from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt

from modules.joanmodules import JOANModules
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from process.statesenum import State
from process import News
from modules.dataplotter.action.dataplottersettings import PlotWindows
from modules.dataplotter.action.dataplottersettings import LineTypes
from modules.dataplotter.action.dataplottersettings import LineColors

class CreateTreeWidgetDialog(QtWidgets.QDialog):
    """
    Creates a recursive treewidget from the available news-items from all initialized modules
    except for the Data Recorder and Data Plotter
    The dialog is shown and editable in the Data Plotter Settings part
    """
    def __init__(self, parent=None, module_action=None, tree_widget=None):
        """
        :param module_action: contains all action performaed on this dialog and settings
        :param tree_widget: the tree which is built up
        :param parent:
        """
        super().__init__(parent)

        self.module_action = module_action
        self.tree_widget = tree_widget

    def make_tree(self):
        """
        The tree is created here recursively with use of the available variables
        in the dataplotter settings
        """
        for module_key, module_news in self.module_action.settings.variables_to_save.items():
            if module_news:   # show only modules with news

                self._create_tree_item(self, self.tree_widget, module_key, module_news)
        self.tree_widget.expandAll()

    @staticmethod
    def _create_tree_item(self, parent, key, value):
        """
        Tree-items are created here.
        :param parent: parent of the current key/value
        :param key: current used key
        :param value: current used value
        """
        if isinstance(value, dict) and str(PlotWindows.KEY) not in value.keys():
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))

            for inner_key, inner_value in value.items():
                CreateTreeWidgetDialog._create_tree_item(self, item, inner_key, inner_value)
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, Qt.DisplayRole, str(key))

            combo_box_plot_window = QtWidgets.QComboBox()
            for plot_window in self.module_action.settings.picklist_plot_windows:
                combo_box_plot_window.addItem(plot_window)
            combo_box_plot_window.setCurrentIndex(combo_box_plot_window.findText(value.get(str(PlotWindows.KEY))))
            slot_lambda_plot_window = lambda: self.handler(item, str(combo_box_plot_window.currentText()), str(PlotWindows.KEY))
            combo_box_plot_window.currentIndexChanged.connect(slot_lambda_plot_window)
            
            if value.get(str(PlotWindows.KEY)) != str(PlotWindows.NOPLOT):
                combo_box_line_type = QtWidgets.QComboBox()
                for line_type in self.module_action.settings.picklist_line_types:
                    combo_box_line_type.addItem(line_type)
                combo_box_line_type.setCurrentIndex(combo_box_line_type.findText(value.get(str(LineTypes.KEY))))
                slot_lambda_line_type = lambda: self.handler(item, str(combo_box_line_type.currentText()), str(LineTypes.KEY))
                combo_box_line_type.currentIndexChanged.connect(slot_lambda_line_type)
                
                combo_box_line_color = QtWidgets.QComboBox()
                for line_color in self.module_action.settings.picklist_line_colors:
                    combo_box_line_color.addItem(line_color)
                combo_box_line_color.setCurrentIndex(combo_box_line_color.findText(value.get(str(LineColors.KEY))))
                slot_lambda_line_color = lambda: self.handler(item, str(combo_box_line_color.currentText()), str(LineColors.KEY))
                combo_box_line_color.currentIndexChanged.connect(slot_lambda_line_color)

                self.tree_widget.setItemWidget(item, 1, combo_box_plot_window)
                self.tree_widget.setItemWidget(item, 2, combo_box_line_type)
                self.tree_widget.setItemWidget(item, 3, combo_box_line_color)
            else:
                self.tree_widget.setItemWidget(item, 1, combo_box_plot_window)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem)
    def handler(self, item, choosen_value, combo_box):
        """
        Handles a click on a combo box object in the tree widget
        This action saves the choosen settings using the module_action module as given in the constructor
        This action also recreate the QTreeWidget (for immediate feedback on choosen plot window)
        :param item: clicked QTreeWidgetItem object
        :param choosen_value: value within the combo box
        :param combo_box: focussed QComboBox object
        """
        texts = [choosen_value, combo_box]
        while item is not None:
            texts.append(item.text(0))
            item = item.parent()

        texts.reverse()  # easier to handle
        if self.module_action.settings.variables_to_save.get(texts[0]) is None:
            self.module_action.settings.variables_to_save[texts[0]] = {}
        temp_dict = self.module_action.settings.variables_to_save.get(texts[0])
        for key in texts[1:-2]:
            if temp_dict.get(key) is None:
                temp_dict[key] = {}
            temp_dict = temp_dict.get(key)
        temp_dict[texts[-2]] = texts[-1]

        self.module_action.handle_tree_widget_click()  # save settings
        
        # redraw treeWidget
        self.tree_widget.clear()
        self.make_tree()


class DataplotterDialog(JoanModuleDialog):
    """
    Builts the dialog used for the Data Plotter and shows it on the inherited dialog
    Inherits the dialog from the JoanModuleDialog
    """
    def __init__(self, module_action: JoanModuleAction, parent=None):
        """
        :param module_action: contains the Datarecorder Action class
        :param parent:
        """
        super().__init__(module=JOANModules.DATA_PLOTTER, module_action=module_action, parent=parent)

        self.module_action.state_machine.add_state_change_listener(self._handle_module_specific_state)
        self.module_action.state_machine.set_entry_action(State.READY, self.create_tree_widget)

        # get news items
        self.news = News()

        # Settings
        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Dataplotter Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Dataplotter Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)
        # load/save file
        self.load_settings.setEnabled(True)
        self.save_settings.setEnabled(False)

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

    def create_tree_widget(self):
        """
        Creates treewidget from settings when starting the module using a separate CreateTreeWidgetDialog class
        """
        self.module_widget.treeWidget.clear()
        create_treewidget_dialog = CreateTreeWidgetDialog(module_action=self.module_action,
                                                          tree_widget=self.module_widget.treeWidget)
        create_treewidget_dialog.make_tree()

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
                # load/save file
                self.load_settings.setEnabled(False)
                self.save_settings.setEnabled(True)
                self.state_widget.input_tick_millis.setEnabled(False)
                self.state_widget.input_tick_millis.setStyleSheet("color: black;  background-color: lightgrey")

            if current_state is State.IDLE:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(False)
                # load/save file
                self.load_settings.setEnabled(True)
                self.save_settings.setEnabled(False)
                self.state_widget.input_tick_millis.setEnabled(True)
                self.state_widget.input_tick_millis.setStyleSheet("color: black;  background-color: white")

            if current_state is State.RUNNING:
                self.state_widget.btn_start.setEnabled(False)
                self.state_widget.btn_stop.setEnabled(True)
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
