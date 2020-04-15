import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from process.joanmoduleaction import JoanModuleAction
from modules.joanmodules import JOANModules


class JoanModuleDialog(QtWidgets.QDialog):

    def __init__(self, module: JOANModules, module_action: JoanModuleAction, parent=None):
        super().__init__(parent)

        self.module_action = module_action

        self.setLayout(QtWidgets.QVBoxLayout(self))

        self.state_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/statewidget.ui"))
        self.layout().addWidget(self.state_widget)

        self.module_widget = uic.loadUi(module.ui_file)
        self.layout().addWidget(self.module_widget)

        self.state_widget.btnStart.clicked.connect(self._button_start_clicked)
        self.state_widget.btnStop.clicked.connect(self._button_stop_clicked)

        self.setWindowTitle(str(module))
        self.state_widget.inputTickMillis.setPlaceholderText(str(self.module_action.millis))

    def _button_start_clicked(self):
        self.module_action.start_pulsar()
        self.state_widget.inputTickMillis.setEnabled(False)
        self.state_widget.inputTickMillis.clear()
        self.state_widget.inputTickMillis.clearFocus()
        self.state_widget.inputTickMillis.setPlaceholderText(str(self.module_action.millis))

    def _button_stop_clicked(self):
        self.module_action.stop_pulsar()
        self.state_widget.inputTickMillis.setEnabled(True)
        self.state_widget.inputTickMillis.clear()
        self.state_widget.inputTickMillis.setPlaceholderText(str(self.module_action.millis))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    callback_1 = lambda: print('Hello World')
    action = JoanModuleAction(JOANModules.DATA_RECORDER, callbacks=[callback_1])

    dialog = JoanModuleDialog(JOANModules.DATA_RECORDER, action)

    dialog.show()

    callback_2 = lambda: print('Olger is cool!')
    action.add_callback(callback_2)
    action.remove_callback(callback_2)
    action.add_callback(callback_2)

    app.exec_()
