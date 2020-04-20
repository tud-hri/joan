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
    JOANMENUWINDOW.add_module(JOANModules.TEMPLATE)
    JOANMENUWINDOW.add_module(JOANModules.DATA_RECORDER)
    JOANMENUWINDOW.add_module(JOANModules.FEED_BACK_CONTROLLER)
    JOANMENUWINDOW.add_module(JOANModules.CARLA_INTERFACE)
    JOANMENUWINDOW.add_module(JOANModules.HARDWARE_MANAGER)

    # # printing widget folders
    # WIDGETFOLDERS = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modules"))
    # for widgetfolder in WIDGETFOLDERS:
    #     if widgetfolder not in ('__pycache__', 'interface', 'template', 'menu', '__init__.py'):
    #         module = '%s%s' % (widgetfolder.title(), 'Widget')
    #         print(module)

    APP.exec_()
