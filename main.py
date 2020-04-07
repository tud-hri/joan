"""Main script
    Intantiates classes by name. The classes, however MUST already exist in globals.
    That is why classes have already been imported using a wildcard (*)
    Make sure that the requested class are also in widgets/__init__.py 
"""

import sys
import traceback
# import qdarkgraystyle

from PyQt5 import QtWidgets

# from modules.joanmenu import JOANMenuWidget
from modules import *
from process import Status
from process import MasterStates

if __name__ == '__main__':

    APP = QtWidgets.QApplication(sys.argv)

    JOANMENU = JOANMenuWidget()
    JOANMENU._show()

    # adding modules (instantiates them too)
    JOANMENU.addModule('DatarecorderWidget')
    JOANMENU.addModule('DatarecorderWidget')
    

    # # printing widget folders
    # WIDGETFOLDERS = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "modules"))
    # for widgetfolder in WIDGETFOLDERS:
    #     if widgetfolder not in ('__pycache__', 'interface', 'template', 'menu', '__init__.py'):
    #         module = '%s%s' % (widgetfolder.title(), 'Widget')
    #         print(module)

    APP.exec_()
