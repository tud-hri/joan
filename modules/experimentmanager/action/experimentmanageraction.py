from PyQt5 import QtCore

from modules.joanmodules import JOANModules
from process.joanmoduleaction import JoanModuleAction
from .states import ExperimentManagerStates

# Used for Settings
import os
from process.settings import ModuleSettings
from process.settings import Settings
import json
from json import JSONDecodeError


class ExperimentManagerAction(JoanModuleAction):
    def __init__(self, master_state_handler, millis=100):
        super().__init__(module=JOANModules.EXPERIMENT_MANAGER, master_state_handler=master_state_handler, millis=millis)

        self.module_state_handler.request_state_change(ExperimentManagerStates.EXPERIMENTMANAGER.READY)

        self.data = {}
        self.write_news(news=self.data)

        #self.settings_object = ModuleSettings(file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'default_experiment_settings.json'))
        self.settings_object = ModuleSettings(file=os.path.join('.', 'default_experiment_settings.json'))
        self.settings = self.settings_object.read_settings()
        self.update_settings(self.settings)                                                                                                    
        print ('a a a', self.settings)

        # create/get default experiment_settings
        self.default_experiment()
        self.experiment_settings = {}  # will contain experiment_settings
        self.condition_names = []      # will contain condition_names for use in getting correct settings

        # TODO: weghalen
        '''
            current_settings = self.settings_object and self.settings_object.read_settings() or {'data': {}}

            if module_object.name not in current_settings['data'].keys():
                current_settings['data'].update({module_object.name: {}})
                
                # TODO: is nu alleen voorbeeld met 1 module
                # TODO: dit hoort eigenlijk thuis in feedbackcontroller
                # TODO: daarna kan het in de Experiment module overruled worden
                if module_object.name == 'FEED_BACK_CONTROLLER':
                    default_dict = {}
                    fdca_dict = {}
                    fdca_dict['K_SW'] = 0.0
                    fdca_dict['K_psi'] = -0.045
                    fdca_dict['K_y'] = 0.12
                    fdca_dict['K_FF'] = 1.0
                    fdca_dict['K_FB'] = 1.0
                    fdca_dict['K_FF_BB'] = 1.0
                    fdca_dict['K_LoHA'] = 0.0
                    fdca_dict['K_LoHA_min'] = 0.01
                    fdca_dict['K_LoHA_max'] = 3.0

                    condition_dict = {}
                    test_aan_dict = {}
                    test_noaan_dict = {}
                    test_aan_dict['idss_type'] = 16
                    test_noaan_dict['idss_type'] = 0
                    condition_dict['Test_AAN'] = test_aan_dict
                    condition_dict['Test_noAAN'] = test_noaan_dict
                    default_dict['FDCA'] = fdca_dict
                    item_dict_feedbackcontroller['default'] = default_dict
                    item_dict_feedbackcontroller['condition'] = condition_dict
                self.settings_object.write_settings(group_key=module_object.name, item=item_dict_feedbackcontroller, filter=self.get_available_module_settings())
                #settings = self.get_module_settings(module=channel)
                #print(settings)
        '''

    def do(self):
        """
        This function is called every controller tick of this module implement your main calculations here
        """
        # self.write_news(news=self.data)

    def initialize(self):
        """
        This function is called before the module is started
        """
        pass

    def start(self):
        try:
            self.module_state_handler.request_state_change(ExperimentManagerStates.EXPERIMENTMANAGER.RUNNING)
        except RuntimeError:
            return False
        return super().start()

    def stop(self):
        try:
            self.module_state_handler.request_state_change(ExperimentManagerStates.EXPERIMENTMANAGER.STOPPED)
        except RuntimeError:
            return False
        return super().stop()

    def initialize_condition(self, condition_nr):
        '''Initialize JOAN for the chosen condition'''
        print('settings for condition '+str(condition_nr))
        print(self.condition_names)
        if 'condition' in self.experiment_settings.keys():
            for condition in self.experiment_settings['condition']:
                if 'name' in condition.keys():
                    if self.condition_names[condition_nr] == condition['name']:
                        self._set_default_settings_in_singleton()
                        self._set_condition_settings_in_singleton(condition)

    def load_experiment(self, experiment_settings_filenames):
        '''All the action stuff for loading a new experiment settings file'''
        print('loading experiment_settings_file: '+str(experiment_settings_filenames))
        experiment_settings_filename = experiment_settings_filenames
        if type(experiment_settings_filename) == list:
            for element in experiment_settings_filename:
                experiment_settings_filename = element

        try:
            with open(experiment_settings_filename, 'r') as experiment_settings_file:
                self.experiment_settings = json.load(experiment_settings_file)
        except JSONDecodeError as inst:
            return '%s line: %s column: %s, characterposition: %s' % (inst.msg, inst.lineno, inst.colno, inst.pos)
        return self.experiment_settings

    def default_experiment(self):
        """Creates a default_experiment_settings_file in JSON format with all settings from all modules"""
        for module_object in JOANModules:
            print(module_object.name)
            #module_settings_object = self.get_module_settings(module=module_object)
            module_settings = self.get_module_settings(module=module_object)
            self.item_dict = {}
            print(type(module_settings)) # != dict:
            #    module_settings = module_settings_object.read_settings()
            try:
                self.item_dict = module_settings['data'][module_object.name]
            except KeyError as inst:
                print(inst)
                #return False
            self.settings_object.write_settings(group_key=module_object.name, item=self.item_dict)
        return True

    def get_experiment_conditions(self):
        if 'condition' in self.experiment_settings.keys():
            for condition in self.experiment_settings['condition']:
                if 'name' in condition.keys():
                    self.condition_names.append(condition['name'])
        return self.condition_names

    def _set_default_settings_in_singleton(self):
        if 'data' in self.settings.keys():
            default_settings = self.settings['data']
            #self._update_singleton_settings(data=default_settings)



    def _set_condition_settings_in_singleton(self, condition):
        #print('a a a', condition)
        if 'data' in self.settings.keys():
            update_settings = self.settings['data']
            for joan_module in JOANModules:
                if joan_module.name in update_settings.keys() and joan_module.name in condition.keys():
                    item_keys = update_settings[joan_module.name].keys()
                    for item in item_keys:
                        if item in condition[joan_module.name].keys():
                            update_settings[joan_module.name][item] = condition[joan_module.name][item]
            self._update_singleton_settings(data=update_settings)


    def _update_singleton_settings(self, data={}):
        for joan_module in JOANModules:
            if (joan_module.name in data.keys()):
                settings = data[joan_module.name]

                print('1 1 1', self.singleton_settings.get_settings(joan_module))

                self.singleton_settings.update_settings(joan_module, settings)
                print('2 2 2', self.singleton_settings.get_settings(joan_module))

