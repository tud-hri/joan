from PyQt5 import QtWidgets, QtCore, QtGui
from .previewconditiondialog_ui import Ui_Dialog


class PreviewConditionDialog(QtWidgets.QDialog):
    def __init__(self, condition, parent=None):
        super().__init__(parent)

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(condition.name)

        for key, value in condition.diff.items():
            self._create_tree_item(self.ui.treeWidget, key, value)
        self.show()

    @staticmethod
    def _create_tree_item(parent, key, value):
        if isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, str(key))

            for inner_key, inner_value in value.items():
                PreviewConditionDialog._create_tree_item(item, inner_key, inner_value)
            return item
        if isinstance(value, list):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, key)

            for index, inner_value in enumerate(value):
                PreviewConditionDialog._create_tree_item(item, index, inner_value)
            return item
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, str(key))
            item.setData(1, 0, value)
            return item
