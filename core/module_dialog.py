import os

from PyQt5 import QtWidgets, uic, QtCore

from core.module_manager import ModuleManager
from core.statesenum import State
from modules.joanmodules import JOANModules


class ModuleDialog(QtWidgets.QDialog):
    """
    Base class for module dialogs, inherits from QDialog
    """
    # signal when dialog is closed
    closed = QtCore.pyqtSignal()


    def __init__(self, module: JOANModules, module_manager: ModuleManager, parent=None):
        super().__init__(parent=None)

        # reference to the manager class of this module
        self.module_manager = module_manager

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.setWindowTitle(str(module))

        # state widget
        self._state_widget = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/state_widget.ui"))
        self.layout().addWidget(self._state_widget)

        # setup module-specific widget
        self._module_widget = uic.loadUi(module.ui_file)
        self.layout().addWidget(self._module_widget)

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




        # connect to module manager's state machine
        self.module_manager.state_machine.add_state_change_listener(self._handle_state_change)

        # update timer
        self.update_timer = QtCore.QTimer()
        self.update_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.update_timer.setInterval(100)  # 10 Hz update
        self.update_timer.timeout.connect(self.update_dialog)



    def update_dialog(self):
        """
        Called by the update timer.
        Use to update the module dialog
        :return:
        """

    def start(self):
        """
        Start timer
        :return:
        """
        if not self.update_timer.isActive():
            self.update_timer.start()

    def _handle_state_change(self):
        """
        Handle state change, registered in the module manager's state machine
        :return:
        """
        # make sure we can only load and save settings in the stopped state:
        if self.module_manager.state_machine.current_state == State.STOPPED:
            self.load_settings.setEnabled(True)
            self.load_settings.blockSignals(False)
            self.save_settings.setEnabled(True)
            self.save_settings.blockSignals(False)
        else:
            self.load_settings.setEnabled(False)
            self.load_settings.blockSignals(True)
            self.save_settings.setEnabled(False)
            self.save_settings.blockSignals(True)

        if hasattr(self, '_state_widget'):
            current_state = self.module_manager.state_machine.current_state
            message = self.module_manager.state_machine.state_message

            # update the state label
            self._state_widget.lbl_module_state.setText(str(current_state))
            self._state_widget.lbl_state_message.setText(message)


            if current_state is State.RUNNING:
                self._state_widget.lbl_module_state.setStyleSheet("background: lightgreen;")
            elif current_state is State.INITIALIZED:
                self._state_widget.lbl_module_state.setStyleSheet("background: lightblue;")
            elif current_state is State.READY:
                self._state_widget.lbl_module_state.setStyleSheet("background: yellow;")
            elif current_state is State.ERROR:  # an Error state
                self._state_widget.lbl_module_state.setStyleSheet("background: red;")
            elif current_state is State.STOPPED:
                self._state_widget.lbl_module_state.setStyleSheet("background: orange;")




    def _load_settings(self):
        """
        Loads settings from json file.
        :return:
        """
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings',
                                                                         os.path.join(self.module_manager.module_path),
                                                                         filter='*.json')
        if settings_file_to_load:
            self.module_manager.load_from_file(settings_file_to_load)

    def _save_settings(self):
        """
        Saves settings to json file
        :return:
        """
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings',
                                                                   self.module_manager.settings_filename,
                                                                   filter='*.json')
        if file_to_save_in:
            self.module_manager.module_settings.save_to_file(file_to_save_in)

    def toggle_show_close(self):
        if self.isVisible():
            self.close()
        else:
            self.show()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
