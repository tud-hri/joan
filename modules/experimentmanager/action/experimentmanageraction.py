from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import ExperimentManagerStates

# Used for Settings
import os
from process.settings import ModuleSettings
from process.settings import Settings
import json
import copy
from json import JSONDecodeError


class ExperimentManagerAction(JoanModuleAction):
    def __init__(self, millis=100):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, millis=millis)
    #def __init__(self, master_state_handler, millis=100):
    #    super().__init__(module=JOANModules.EXPERIMENT_MANAGER, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(ExperimentManagerStates.EXEC.READY)

        self.data = {}
        self.write_news(news=self.data)

        # set factory settings per module, must be called before self.write_default_experiment()
        self._set_factory_settings_in_singleton()

        # create/get default experiment_settings
        self.my_file = os.path.join('.', 'default_experiment_settings.json')
        # First remove current file
        if os.path.exists(self.my_file):
            os.remove(self.my_file)
        self.settings_object = ModuleSettings(file=self.my_file)
        self.settings = self.settings_object.read_settings()
        self.settings.update(self._get_attention_message())
        self.share_settings(self.settings)

        self.write_default_experiment()  # maybe used as an example for experiment conditions
        self.experiment_settings = {}    # will contain experiment_settings
        self.condition_names = []        # will contain condition_names for use in getting correct settings

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        # self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        try:
            self.module_state_handler.request_state_change(ExperimentManagerStates.INIT.INITIALIZING)
        except RuntimeError:
            return False
        return super().initialize()

    def start(self):
        try:
            self.module_state_handler.request_state_change(ExperimentManagerStates.EXEC.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(ExperimentManagerStates.EXEC.STOPPED)
        except RuntimeError:
            return False
        return super().stop()

    def initialize_condition(self, condition_nr):
        """Initialize JOAN for the chosen experiment with user-defined conditions
        First: The default settings per module are set to the initial values
        These initial values can be found in the 'def __init__' of a module
        Second: The modified settings as found in the condition-part will replace the initial value
        These modified values will be read by a module in the 'def initialize' of a module 
        """
        self._set_default_settings_in_singleton()  # Set factory settings per module in working-settings
        self.write_default_experiment()            # create default settings file with content of all modules
        if 'condition' in self.experiment_settings.keys():
            for condition in self.experiment_settings['condition']:
                if 'name' in condition.keys():
                    if self.condition_names[condition_nr] == condition['name']:
                        self._set_condition_settings_in_singleton(condition)

    def load_experiment(self, experiment_settings_filenames):
        """All the action stuff for loading a new experiment settings file
        called from 'menu->file->load'
        """
        experiment_settings_filename = experiment_settings_filenames
        if isinstance(experiment_settings_filename, list):
            for element in experiment_settings_filename:
                experiment_settings_filename = element

        self.condition_names.clear()
        try:
            with open(experiment_settings_filename, 'r') as experiment_settings_file:
                self.experiment_settings = json.load(experiment_settings_file)
        except JSONDecodeError as inst:
            return '%s line: %s column: %s, characterposition: %s' % (inst.msg, inst.lineno, inst.colno, inst.pos)
        except IsADirectoryError as inst:
            return 'Error: %s , %s is a directory' % (inst, experiment_settings_filename)

        # fill condition_names again with the conditions ins self.experiment_settings (just loaded)
        if 'condition' in self.experiment_settings.keys():
            for condition in self.experiment_settings['condition']:
                if 'name' in condition.keys():
                    self.condition_names.append(condition['name'])

        return self.experiment_settings

    def write_default_experiment(self):
        """Creates a default_experiment_settings_file in JSON format
        with all settings from all modules
        """
        # First remove current file
        if os.path.exists(self.my_file):
            os.remove(self.my_file)
        # Create new file
        for module_object in JOANModules:
            module_factory_settings = self.get_module_factory_settings(module=module_object)
            self.item_dict = {}
            try:
                self.item_dict = module_factory_settings['data'][module_object.name]
            except KeyError:
                pass
                #print('Info: Module %s has no settings' % module_object.name)
            except TypeError:  # Module settings are of new style, TODO: remove old style above
                self.item_dict = module_factory_settings.as_dict()

            self.settings_object.write_settings(group_key=module_object.name, item=self.item_dict)

    def get_experiment_conditions(self):
        return self.condition_names

    def _get_attention_message(self):
        attention_message = {}
        data_part = {}
        condition_part = {}
        data_part["ALTER"] = "do NOT alter this data-part for this file is automatically generated"
        data_part["PURPOSE"] = "an example for the condition-settings to be altered"
        condition_part["ALTER"] = "please do, that is the purpose"
        condition_part["PURPOSE"] = "set predefined conditions for your experiment"

        condition_part_example_1_module = {}
        condition_part_example_1_module["TEMPLATE"] = {"steer_sensitivity": 12, "throttle_sensitivity": 5}
        condition_part_example_1_module["name"] = "experiment 1"
        condition_part_example_2_module = {}
        condition_part_example_2_module["TEMPLATE"] = {"steer_sensitivity": 10, "throttle_sensitivity": 5}
        condition_part_example_2_module["name"] = "experiment 2"
        
        condition_part_example = []
        condition_part_example.append(condition_part_example_1_module)
        condition_part_example.append(condition_part_example_2_module)

        condition_part["condition"] = condition_part_example

        attention_message["data-part"] = data_part
        attention_message["condition-part"] = condition_part

        return {"ATTENTION - Copy this file and set conditions for your experiment": attention_message, "condition": [{"name": "No Experiment condition defined"}]}

    def _set_factory_settings_in_singleton(self):
        """ Sets factory settings in settings_singleton for each module at the start of the program"""
        for module_object in JOANModules:
            module_settings = self.get_module_settings(module=module_object)
            module_factory_settings = copy.deepcopy(module_settings)
            self.singleton_settings.update_factory_settings(module_object, {})
            self.singleton_settings.update_factory_settings(module_object, module_factory_settings)

    def _set_default_settings_in_singleton(self):
        """ Sets the default settings per module back to the module 'def __init__' settings"""
        for module_object in JOANModules:
            module_factory_settings = self.get_module_factory_settings(module=module_object)
            module_settings = copy.deepcopy(module_factory_settings)
            self.singleton_settings.share_settings(module_object, {})
            self.singleton_settings.share_settings(module_object, module_settings)

    def _set_condition_settings_in_singleton(self, condition):
        """ Set the condition settings per module, must be read through the module 'def initialize'
        data will overrule the default settings
        """
        for joan_module in JOANModules:
            update_settings = copy.deepcopy(self.singleton_settings.get_factory_settings(joan_module))
            if 'data' in update_settings.keys():
                update_settings = update_settings['data']
            try:
                if joan_module.name in condition.keys():
                    item_keys = update_settings[joan_module.name].keys()
                    for item in item_keys:
                        if item in condition[joan_module.name].keys():
                            update_settings[joan_module.name][item] = condition[joan_module.name][item]
                            self.singleton_settings.share_settings(joan_module, update_settings)
            except KeyError:
                pass