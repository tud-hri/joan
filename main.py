"""Main script
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)
    Make sure that the requested class are also in widgets/__init__.py 
"""
import sys

from PyQt5 import QtWidgets

from core import JoanHQAction, JoanHQWindow
from modules.joanmodules import JOANModules

if __name__ == '__main__':
    APP = QtWidgets.QApplication(sys.argv)

    JOANHQACTION = JoanHQAction()
    JOANHQWINDOW = JoanHQWindow(JOANHQACTION)
    JOANHQACTION.window = JOANHQWINDOW
    JOANHQWINDOW.show()

    # adding modules (instantiates them too)
    JOANHQACTION.add_module(JOANModules.TEMPLATE_MP, time_step=1.0)

    APP.exec_()
