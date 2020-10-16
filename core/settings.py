import json
from json import JSONDecodeError
import copy
from modules.joanmodules import JOANModules


class Settings:
    """
    The Settings class is a singleton that holds settings of module, 
    so they can be used from Experiment classes, using the module_key
    """
    instance = None

    def __new__(cls):
        if not cls.instance:
            cls.instance = object.__new__(Settings)
            ''' TODO: Remove this, because apparenlty not used (20201015)
            cls._factory_settings = {}
            '''
            cls._settings = {}

        return cls.instance

    ''' TODO: Remove this, because apparenlty not used (20201015)
    def update_factory_settings(self, module: JOANModules, module_settings):
        """
        Update the default (factory) settings
        :param module: module to update factory settings for
        :param module_settings: new default settings for the module
        :return:
        """
        self._factory_settings.update({module: module_settings})
    '''

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

    ''' TODO: Remove this, because apparenlty not used (20201015)
    def get_factory_settings(self, module: JOANModules):
        try:
            return self._factory_settings[module]
        except KeyError:
            return {}
    '''

    @property
    def all_settings(self):
        return self._settings

    @property
    def all_settings_keys(self):
        return self._settings.keys()
