import abc
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess


class Scenario:
    @abc.abstractmethod
    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass
