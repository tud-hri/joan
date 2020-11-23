import os

from PyQt5 import QtWidgets
import glob
from .newexperimentdialog_ui import Ui_Dialog


class NewExperimentDialog(QtWidgets.QDialog):
    """
    New experiment dialog is opened when the user creates a new experiment
    The dialog asks the user to select the modules that need to be taken into account,
    and the file name and location
    """

    def __init__(self, all_modules_in_settings, parent=None, path=''):
        super().__init__(parent)
        self.checkboxes = {}
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self._fill_module_box(all_modules_in_settings)
        self.ui.browsePushButton.clicked.connect(self._browse_file)

        self.file_path = ""
        self.path = path
        self.modules_to_include = []

        self.show()

    def _fill_module_box(self, all_modules_in_settings):
        """
        Create list with checkboxes for selecting modules in experiment
        :param all_modules_in_settings: list with all modules (in the settings singleton)
        :return:
        """
        for module in all_modules_in_settings:
            checkbox = QtWidgets.QCheckBox(str(module))
            self.checkboxes[module] = checkbox
            self.ui.modulesGroupBox.layout().addWidget(checkbox)

    def _browse_file(self):
        """
        Select experiment json path and name
        :return:
        """
        path_to_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save experiment to...",
                                                                os.path.join(self.path, 'experiments'),
                                                                filter='*.json')
        basename = os.path.basename(path_to_file)
        file_name = os.path.splitext(basename)
        if path_to_file:
            self.ui.fileLineEdit.setText(file_name[0])

    def accept(self):
        """
        User clicked accept, check which modules to include and the selected path and name
        :return:
        """
        file_name = self.ui.fileLineEdit.text()
        accept_bool = True
        if file_name != '':
            self.file_path = os.path.join(self.path, 'experiments/' + file_name + '.json')

        self.modules_to_include = []
        for module, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                self.modules_to_include.append(module)

        if self.file_path != '' and self.modules_to_include:
            for fname in glob.glob(self.file_path):
                if (os.path.basename(self.file_path)[:-5]) == (os.path.basename(fname)[:-5]):
                    reply = QtWidgets.QMessageBox.question(self, "Warning",
                                                           "This filename already exists in the folder, do you wish to overwrite?.")
                    if (reply == QtWidgets.QMessageBox.Yes):
                        accept_bool = True
                    else:
                        accept_bool = False
                else:
                    accept_bool = True
            if accept_bool:
                super().accept()
        elif self.file_path and self.modules_to_include == []:
            QtWidgets.QMessageBox.warning(self, "Warning",
                                          "Please supply select modules to include.")
        elif self.file_path == '' and self.modules_to_include:
            QtWidgets.QMessageBox.warning(self, "Warning",
                                          "Please include a filename.")
        elif self.file_path == '' and self.modules_to_include == []:
            QtWidgets.QMessageBox.warning(self, "Warning",
                                          "Please supply the selected modules to include and provide a valid filename.")
