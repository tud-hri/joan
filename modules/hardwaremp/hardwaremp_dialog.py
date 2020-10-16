from core.module_dialog import ModuleDialog
from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from PyQt5 import uic

import os


class HardwareMPDialog(ModuleDialog):
    def __init__(self, module_manager: ModuleManager, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, module_manager=module_manager, parent=parent)
        self._input_type_dialog = uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "uis/inputtype.ui"))
        self._module_widget.btn_add_hardware.clicked.connect(self._input_type_dialog.show)


