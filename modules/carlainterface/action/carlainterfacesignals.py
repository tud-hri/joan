from PyQt5.QtCore import pyqtSignal

from core.joanmodulesignals import JoanModuleSignal


class CarlaInterfaceSignals(JoanModuleSignal):

    respawn_all_agents = pyqtSignal()  # respawn all agents
    respawn_agent = pyqtSignal(int)  # respawn agent, integer is the ID of the agent

    def __init__(self, module_enum, module_action):
        super().__init__(module_enum, module_action)
