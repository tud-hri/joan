from modules.joanmodules import JOANModules
"""
Holds settings of every module to be used by the experimentmanager
"""


class Settings:
    """
    The Settings class is a singleton that holds settings of all modules,
    so they can be used from Experiment classes, using the module_key
    """
    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = object.__new__(Settings)
            cls._settings = {}

        return cls.instance

    def update_settings(self, module: JOANModules, module_settings):
        """
        Update the settings for a specified module
        :param module: module to update settings for
        :param module_settings: new settings
        :return:
        """
        self._settings.update({module: module_settings})

    def get_settings(self, module: JOANModules):
        try:
            return self._settings[module]
        except KeyError:
            return {}

    @property
    def all_settings(self):
        return self._settings

    @property
    def all_settings_keys(self):
        return self._settings.keys()
