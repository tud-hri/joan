from PyQt5.QtCore import pyqtSignal

from process.joanmodulesignals import JoanModuleSignal


class CarlaInterfaceSignals(JoanModuleSignal):

    respawn_all_agents = pyqtSignal()  # respawn all agents
    respawn_agent = pyqtSignal(int)  # respawn agent, integer is the ID of the agent
