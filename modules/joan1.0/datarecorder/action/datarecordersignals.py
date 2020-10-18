from PyQt5.QtCore import pyqtSignal

from core.joanmodulesignals import JoanModuleSignal


class DataRecorderSignals(JoanModuleSignal):

    prepare_recording = pyqtSignal()
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()

    def __init__(self, module_enum, module_action):
        super().__init__(module_enum, module_action)
