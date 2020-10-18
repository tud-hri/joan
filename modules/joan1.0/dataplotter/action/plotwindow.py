import os
from PyQt5 import QtWidgets
from PyQt5 import uic

class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

    def get_plot_window(self):
        """
        Loads a main window for plots
        :return: a window to show plots 
        """
        try:
            return uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/plot_window.ui"))
        except FileNotFoundError:
            print("Error: Missing %s" % os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/plot_window.ui"))
