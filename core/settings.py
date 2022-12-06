from modules.joanmodules import JOANModules

"""
Holds settings of every module to be used by the experimentmanager
"""

class Settings:
    def __init__(self):
        self._settings = {}

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
            return None

    def remove_settings(self, module: JOANModules):
        """
        Remove module shared variable from News
        :param module: module enum
        :return:
        """
        try:
            del self._settings[module]
        except KeyError as e:
            print('There is no settings yet from', e)

    @property
    def all_settings(self):
        return self._settings

    @property
    def all_settings_keys(self):
        return self._settings.keys()
