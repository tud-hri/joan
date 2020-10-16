import os

from PyQt5 import QtWidgets, uic, QtCore

from core.module_manager import ModuleManager
from core.statesenum import State
from modules.joanmodules import JOANModules


class ModuleDialog(QtWidgets.QDialog):
    # signal when dialog is closed
    closed = QtCore.pyqtSignal()

    def __init__(self, module: JOANModules, module_manager: ModuleManager, parent=None):
        super().__init__(parent=parent)

        # reference to the manager class of this module
        self._module_manager = module_manager

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.setWindowTitle(str(module))

        # menu bar
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.layout().setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu('File')
        self.file_menu.addAction('Close', self.close)
        self.file_menu.addSeparator()
        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.load_settings.setEnabled(True)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)

        self._module_manager.state_machine.add_state_change_listener(self._handle_state_change)

        self._state_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/statewidget.ui"))
        self.layout().addWidget(self._state_widget)

        # setup module-specific widget
        self._module_widget = uic.loadUi(module.ui_file)
        self.layout().addWidget(self._module_widget)

        self.update_timer = QtCore.QTimer()
        self.update_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.update_timer.setInterval(100)  # 50 Hz update
        self.update_timer.timeout.connect(self.update_dialog)

    def update_dialog(self):
        pass

    def start(self):
        if not self.update_timer.isActive():
            self.update_timer.start()

    def _handle_state_change(self):
        """
        Handle state change, registered in the module manager's state machine
        :return:
        """

        if hasattr(self, '_state_widget'):
            current_state = self._module_manager.state_machine.current_state
            message = self._module_manager.state_machine.state_message

            # update the state label
            self._state_widget.lbl_module_state.setText(str(current_state))
            self._state_widget.lbl_state_message.setText(message)

            if current_state is State.RUNNING:
                self._state_widget.lbl_module_state.setStyleSheet("background: green;")
            elif current_state is State.IDLE:
                self._state_widget.lbl_module_state.setStyleSheet("background: orange;")
            elif current_state is State.READY:
                self._state_widget.lbl_module_state.setStyleSheet("background: yellow;")
            elif current_state is State.ERROR:  # an Error state
                self._state_widget.lbl_module_state.setStyleSheet("background: red;")

    def _load_settings(self):
        """
        Loads settings from json file.
        :return:
        """
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings',
                                                                         self._module_manager.settings_filename,
                                                                         filter='*.json')
        if settings_file_to_load:
            self._module_manager.module_settings.load_from_file(settings_file_to_load)

    def _save_settings(self):
        """
        Saves settings to json file
        :return:
        """
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings',
                                                                   self._module_manager.settings_filename,
                                                                   filter='*.json')
        if file_to_save_in:
            self._module_manager.module_settings.save_to_file(file_to_save_in)

    def toggle_show_close(self):
        """Toggle visibility of this dialog"""
        if self.isVisible():
            self.close()
        else:
            self.show()

    def closeEvent(self, event):
        """Override QtDialog's closeEvent, add closed signal"""
        self.closed.emit()
        super().closeEvent(event)
