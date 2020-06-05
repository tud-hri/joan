import json
from json import JSONDecodeError
import copy
from modules.joanmodules import JOANModules


class Settings:
    '''
    The Settings class is a singleton that holds settings of module, 
    so they can be used from Experiment classes, using the module_key
    '''
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(Settings)
            cls._factory_settings = {}
            cls._settings = {}

        return cls.instance

    # def __init__(self, settings_dict):
    #    self._settings.update(settings_dict)

    def update_factory_settings(self, module: JOANModules, module_settings):
        self._factory_settings.update({module: module_settings})

    def update_settings(self, module: JOANModules, module_settings):
        self._settings.update({module: module_settings})

    def get_settings(self, module: JOANModules):
        try:
            return self._settings[module]
        except KeyError:
            return {}

    def get_factory_settings(self, module: JOANModules):
        try:
            return self._factory_settings[module]
        except KeyError:
            return {}

    @property
    def all_settings(self):
        return self._settings

    @property
    def all_settings_keys(self):
        return self._settings.keys()


class ModuleSettings:
    """
    Write and read in JSON Settings format:

    { "data": {
            "groupKey1":{
                "item1": value,
                "item2": value
            },
            "groupKey2":{
                "item1": value,
                "item2": value,
                "item3": value
            }
        }
    }
    """

    def __init__(self, file='settings.json'):
        self._file = file
        self._module_settings = None

    def _filter_settings(self, keys=[]):
        copy_settings = copy.deepcopy(self._module_settings)
        for channel in self._module_settings['data'].keys():
            try:
                channel = channel.name  # get name of enum
            except:
                pass
            if channel not in list(map(lambda x: x.name, keys)):  # iterate through keys, extract name of each module
                del copy_settings['data'][channel]

        self._module_settings = copy.deepcopy(copy_settings)

    def write_settings(self, group_key=None, item=None, filter=[]):
        """
        group_key: the key for a group of items
        item: a dictionary with {key: value}
        filter: if empty, no filtering takes place, if not empty settings are filtered and will only contain module_keys, given in the filter-list
        """
        # if type(result) == str then something went wrong with reading the JSON file
        result = self.read_settings()
        # add/remove/change content to self._module_settings
        # remove settings from removed data
        if len(filter) > 0:
            self._filter_settings(keys=filter)

        # add/change content of self._module_settings
        if group_key and type(result) == dict:
            group_data = {}
            if group_key in self._module_settings['data'].keys():
                group_data = self._module_settings['data'][group_key]
            else:
                self._module_settings['data'][group_key] = group_data
            for item_key in item:
                group_data[item_key] = item[item_key]

            try:
                with open(self._file, 'w') as settings_file:
                    json.dump(self._module_settings, settings_file, sort_keys=True, indent=4)
            except OSError as inst:
                print(inst)
                return False
            return True

        return False

    def read_settings(self):
        """
        read settings and returns a JSON object
        if empty it will return {'data: : {}}
        """
        try:
            with open(self._file, 'r') as module_settings_file:
                self._module_settings = json.load(module_settings_file)
        except JSONDecodeError as inst:
            return inst
        except OSError:
            if self._module_settings is None:
                self._module_settings = {}
                self._module_settings['data'] = {}
        return self._module_settings
