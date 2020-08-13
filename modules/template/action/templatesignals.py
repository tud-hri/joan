from PyQt5.QtCore import pyqtSignal

from process.joanmodulesignals import JoanModuleSignal


class TemplateSignals(JoanModuleSignal):
    # pyqtSignals need to be class attributes...
    my_custom_signal = pyqtSignal()

    # signals can have a parameter (e.g. you can send data with a signal when you emit the signal);
    # in this example type string
    my_custom_signal_str = pyqtSignal(str)
