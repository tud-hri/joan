'''
JSON Settings format:

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
'''
import json
import copy


class Settings:
    '''
    writes and reads settings in JSON format
    '''
    def __init__(self, file='settings.json', *args, **kwargs):
        self._file = file
        self._settings = None

    def _filter(self, keys=[]):
        copySettings = copy.deepcopy(self._settings)
        for channel in self._settings['data'].keys():
            if channel not in keys:
                del copySettings['data'][channel]
        self._settings = copy.deepcopy(copySettings)

    def write(self, groupKey=None, item=None, filter=[]):
        """
        groupKey: the key for a group of items

        item: a dictionary with {key: value}

        filter: if empty, no filtering takes place, if not empty settings are filtered and will only contain moduleKeys, given in the filterList
        """
        self.read()
        # add/remove/change content to self._settings
        # remove settings from removed data
        if len(filter) > 0:
            self._filter(keys=filter)
        # add/change content of self._settings
        if groupKey:
            try:
                groupData = {}
                if groupKey in self._settings['data'].keys():
                    groupData = self._settings['data'][groupKey]
                else:
                    self._settings['data'][groupKey] = groupData
                for itemKey in item:
                    groupData[itemKey] = item[itemKey]

                with open(self._file, 'w') as settingsFile:
                    json.dump(self._settings, settingsFile, sort_keys=True, indent=4)
            except Exception as inst:
                print(inst)
                return False
            return True
        else:
            return False

    def read(self):
        # read settings and return a json object
        try:
            with open(self._file, 'r') as settingsFile:
                self._settings = json.load(settingsFile)
        except Exception as inst:
            if self._settings is None:
                self._settings = {}
                self._settings['data'] = {}
        return self._settings
