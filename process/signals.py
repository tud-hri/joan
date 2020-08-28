from modules.joanmodules import JOANModules


class Signals:
    """
    The Signals class is a singleton that holds all module signals
    Every module has its own signals. Each signal is connected to a function in that module.
    You can use each module's signals to call/trigger a function module
    """
    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = object.__new__(Signals)
            cls._signals = {}

        return cls.instance

    def add_signals(self, module: JOANModules, signals):
        """
        add new signals
        :param module: used as an identifier
        :param signals: JoanModuleSignals object with the
        """
        self._signals.update({module: signals})

    def get_signals(self, module: JOANModules):
        """
        Retrieve the module's signals
        :param module:
        :return: requested signals
        """
        try:
            return self._signals[module]
        except KeyError:
            return {}
