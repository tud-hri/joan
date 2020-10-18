import os

from PyQt5 import QtWidgets

from .newexperimentdialog_ui import Ui_Dialog


class NewExperimentDialog(QtWidgets.QDialog):
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
        for module in all_modules_in_settings:
            checkbox = QtWidgets.QCheckBox(str(module))
            self.checkboxes[module] = checkbox
            self.ui.modulesGroupBox.layout().addWidget(checkbox)

    def _browse_file(self):
        path_to_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save experiment to...",
                                                                os.path.join(self.path, 'experiments'),
                                                                filter='*.json')
        if path_to_file:
            self.ui.fileLineEdit.setText(path_to_file)

    def accept(self):
        self.file_path = self.ui.fileLineEdit.text()

        self.modules_to_include = []
        for module, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                self.modules_to_include.append(module)

        if self.file_path and self.modules_to_include:
            super().accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning",
                                          "Please select at least one module and supply a save path for your experiment.")
