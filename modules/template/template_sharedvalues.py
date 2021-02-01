import multiprocessing as mp

from core.modulesharedvariables import ModuleSharedVariables


class TemplateSharedVariables(ModuleSharedVariables):
    """
    Example module for JOAN
    Can also be used as a template for your own modules.
    """
    def __init__(self):
        super().__init__()
        self._overwrite_with_current_time = mp.Array('c', 30)  # 30=length of string

    @property
    def overwrite_with_current_time(self):
        return str(self._overwrite_with_current_time.value, encoding='utf-8')

    @overwrite_with_current_time.setter
    def overwrite_with_current_time(self, val):
        self._overwrite_with_current_time.value = bytes(val, 'utf-8')
