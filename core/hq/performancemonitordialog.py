import os

from PyQt5 import QtWidgets, QtCore, QtGui, uic
from core.statesenum import State


class PerformanceMonitorDialog(QtWidgets.QDialog):
    def __init__(self, all_instantiated_modules, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/performancemonitor_dialog.ui"), self)

        self.all_instantiated_modules = all_instantiated_modules
        row = 0
        self.module_row_numbers = {}
        for enum, module in all_instantiated_modules.items():
            self.tableWidget.insertRow(row)
            self.module_row_numbers[module] = row
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(enum)))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem("- Hz"))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem("- Hz"))
            self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem("- Hz"))
            row += 1

        self._update_gui()
        self.update_timer = QtCore.QTimer()
        self.update_timer.setSingleShot(False)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self._update_gui)
        self.update_timer.start()

        self.show()

    def _update_gui(self):
        for enum, module in self.all_instantiated_modules.items():
            row = self.module_row_numbers[module]
            if module.shared_variables and module.state_machine.current_state is State.RUNNING:
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem("%.1f Hz" % module.shared_variables.running_frequency))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem("%.1f Hz" % (1000 / module._time_step_in_ms)))
                try:
                    self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem("%.1f Hz" % (1e9 / module.shared_variables.execution_time)))
                except ZeroDivisionError:
                    self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem("inf Hz"))

                if module.shared_variables.running_frequency < (1000 / module._time_step_in_ms) * 0.95 and module.shared_variables.running_frequency:
                    self.tableWidget.item(row, 1).setBackground(QtGui.QBrush(QtCore.Qt.red))
                else:
                    self.tableWidget.item(row, 1).setBackground(QtGui.QBrush(QtCore.Qt.NoBrush))

            else:
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem("- Hz"))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem("%.1f Hz" % (1000 / module._time_step_in_ms)))
                self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem("- Hz"))


