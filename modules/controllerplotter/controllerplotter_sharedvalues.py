import multiprocessing as mp
from ctypes import *

from core.modulesharedvariables import ModuleSharedVariables


class ControllerPlotterSharedVariables(ModuleSharedVariables):
    def __init__(self):
        super().__init__()

