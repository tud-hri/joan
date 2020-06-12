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
    #JOANHQACTION.add_module(JOANModules.CARLA_INTERFACE, millis=50)
    #JOANHQACTION.add_module(JOANModules.HARDWARE_MANAGER, millis=10)
    JOANHQACTION.add_module(JOANModules.TEMPLATE) 
    #JOANHQACTION.add_module(JOANModules.DATA_RECORDER)
    # JOANHQACTION.add_module(JOANModules.FEED_BACK_CONTROLLER)

    # add the EXPERIMENT_MANAGER last because this one collects settings from JOAN modules that are already loaded
    #JOANHQACTION.add_module(JOANModules.EXPERIMENT_MANAGER)

    APP.exec_()

