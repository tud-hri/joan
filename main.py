"""Main script
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)
    Make sure that the requested class are also in widgets/__init__.py 
"""
import sys

from PyQt5 import QtWidgets

from core import HQManager
from modules.joanmodules import JOANModules

if __name__ == '__main__':
    APP = QtWidgets.QApplication(sys.argv)

    JOANHQACTION = HQManager()

    # adding modules (instantiates them too)
    # JOANHQACTION.add_module(JOANModules.TEMPLATE, time_step_in_ms=100)
    JOANHQACTION.add_module(JOANModules.HARDWARE_MANAGER, time_step_in_ms=10)
    # JOANHQACTION.add_module(JOANModules.CARLA_INTERFACE, time_step_in_ms= 10)
    # JOANHQACTION.add_module(JOANModules.HAPTIC_CONTROLLER_MANAGER, time_step_in_ms= 10)
    # JOANHQACTION.add_module(JOANModules.CONTROLLER_PLOTTER, time_step_in_ms=500)
    # JOANHQACTION.add_module(JOANModules.DATA_RECORDER, time_step_in_ms=100)
    # JOANHQACTION.add_module(JOANModules.EXPERIMENT_MANAGER, time_step_in_ms=500)
    JOANHQACTION.add_module(JOANModules.DATA_PLOTTER, time_step_in_ms = 100)

    APP.exec_()
