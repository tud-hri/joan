import os

from PyQt5 import QtWidgets, QtCore, QtGui, uic


class PerformanceMonitorDialog(QtWidgets.QDialog):
    def __init__(self, all_instantiated_modules, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "performancemonitordialog.ui"), self)

        self.all_instantiated_modules = all_instantiated_modules
        row = 0
        self.module_row_numbers = {}
        for enum, module in all_instantiated_modules.items():
            self.tableWidget.insertRow(row)
            self.module_row_numbers[module] = row
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(enum)))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem("%.1f Hz" % module.running_frequency))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem("%.1f Hz" % (1000 / module._millis)))
            row += 1

        self.update_timer = QtCore.QTimer()
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self._update_gui)
        self.update_timer.start()

        self.show()

    def _update_gui(self):
        for enum, module in self.all_instantiated_modules.items():
            row = self.module_row_numbers[module]
            self.tableWidget.item(row, 1).setText("%.1f Hz" % module.running_frequency)
            self.tableWidget.item(row, 2).setText("%.1f Hz" % (1000 / module._millis))
