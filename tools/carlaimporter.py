import sys
import os
import glob
from PyQt5 import QtCore, QtWidgets

all_carla_egg_files = glob.glob(os.path.join(os.getcwd(),
                                             'carla_pythonapi',
                                             'carla-*%d.%d-%s.egg' % (sys.version_info.major,
                                                                      sys.version_info.minor,
                                                                      'win-amd64' if os.name == 'nt' else
                                                                      'linux-x86_64')))
if not all_carla_egg_files:
    msg_box = QtWidgets.QMessageBox()
    msg_box.setTextFormat(QtCore.Qt.RichText)

    msg_box.setText("""
                    <h3> Could not find the carla python API! </h3>
                    <h3> Check whether you copied the egg file correctly, reference:
                <a href=\"https://joan.readthedocs.io/en/latest/setup-carla-windows/\">https://joan.readthedocs.io/en/latest/setup-carla-windows/</a>
                </h3>
                """)
    msg_box.exec()
else:
    sys.path.append(all_carla_egg_files[-1])

import carla
