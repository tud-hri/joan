from PyQt5.QtCore import pyqtSignal

from process.joanmodulesignals import JoanModuleSignal


class DataRecorderSignals(JoanModuleSignal):

    prepare_recording = pyqtSignal()
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()
