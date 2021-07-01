from .scenario import Scenario
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess


class ExamplePrintScenario(Scenario):
    """
    A simple example scenario that checks if a keyboard is added to hardware manager and print a message if this is True. It shows how:
        1) a statement can be checked
        2) some code can be executed once, if True
        3) how other modules can be accessed from a scenario

    """
    def __init__(self):
        super().__init__()

        self.keyboard_message_sent = False

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        if not self.keyboard_message_send:
            for hardware_name in carla_interface_process.shared_variables_hardware.inputs:
                if 'Keyboard' in hardware_name:
                    print('A keyboard is active')
                    self.keyboard_message_sent = True

    @property
    def name(self):
        return 'Print scenario'
