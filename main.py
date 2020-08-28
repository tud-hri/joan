"""Main script
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)
    Make sure that the requested class are also in widgets/__init__.py 
"""
import sys

from PyQt5 import QtWidgets

from modules.joanmodules import JOANModules
from process import JoanHQAction, JoanHQWindow

if __name__ == '__main__':
    APP = QtWidgets.QApplication(sys.argv)

    JOANHQACTION = JoanHQAction()
    JOANHQWINDOW = JoanHQWindow(JOANHQACTION)
    JOANHQACTION.window = JOANHQWINDOW
    JOANHQWINDOW.show()

    # adding modules (instantiates them too)
    JOANHQACTION.add_module(JOANModules.HARDWARE_MANAGER, millis=2)
    JOANHQACTION.add_module(JOANModules.STEERING_WHEEL_CONTROL, millis=2)
    JOANHQACTION.add_module(JOANModules.CARLA_INTERFACE, millis=5)
    JOANHQACTION.add_module(JOANModules.TEMPLATE)
    JOANHQACTION.add_module(JOANModules.DATA_RECORDER, millis=5)
    # JOANHQACTION.add_module(JOANModules.DATA_PLOTTER, millis=2000)

    # add the EXPERIMENT_MANAGER last because this one collects settings from JOAN modules that are already loaded
    JOANHQACTION.add_module(JOANModules.EXPERIMENT_MANAGER)

    APP.exec_()
