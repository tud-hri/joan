from process import State, translate
from process.joanmoduledialog import JoanModuleDialog
from process.joanmoduleaction import JoanModuleAction
from PyQt5 import QtCore
from modules.joanmodules import JOANModules
from modules.template.action.states import TemplateStates
from modules.template.action.templateaction import TemplateAction
import os


class TemplateDialog(JoanModuleDialog):
    def __init__(self, module_action: JoanModuleAction, master_state_handler, parent=None):
        super().__init__(module=JOANModules.TEMPLATE, module_action=module_action, master_state_handler=master_state_handler, parent=parent)
