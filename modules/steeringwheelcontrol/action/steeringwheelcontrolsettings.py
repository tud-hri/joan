import inspect
from enum import Enum

from modules.joanmodules import JOANModules
from process.joanmodulesettings import JoanModuleSettings


class SteeringWheelControlSettings(JoanModuleSettings):
    def __init__(self, module_enum: JOANModules):
        super().__init__(module_enum)

        self.pd_controllers = []
        self.fdca_controllers = []

    def load_from_dict(self, loaded_dict):
        """
        This method overrides the base implementation of loading settings from dicts. This is done because hardware manager has the unique property that
        multiple custom settings classes are combined in a list. This behavior is not supported by the normal joan module settings, so it an specific solution
        to loading is implemented here.

        :param loaded_dict: (dict) dictionary containing the settings to load
        :return: None
        """
        try:
            self.before_load_settings.emit()
            module_settings_to_load = loaded_dict[str(self._module_enum)]
        except KeyError:
            warning_message = "WARNING: loading settings for the " + str(
                self._module_enum) + " module from a dictionary failed. The loaded dictionary did not contain " + str(
                self._module_enum) + " settings."  # + (" It did contain settings for: " + ", ".join(loaded_dict.keys()) if loaded_dict.keys() else "")
            print(warning_message)
            return

        self.pd_controllers = []
        for pdcontroller_settings_dict in module_settings_to_load['pd_controllers']:
            pdcontroller_settings = PDControllerSettings()
            pdcontroller_settings.set_from_loaded_dict(pdcontroller_settings_dict)
            self.pd_controllers.append(pdcontroller_settings)

        self.fdca_controllers = []
        for fdcacontroller_settings_dict in module_settings_to_load['fdca_controllers']:
            fdcacontroller_settings = FDCAControllerSettings()
            fdcacontroller_settings.set_from_loaded_dict(fdcacontroller_settings_dict)
            self.fdca_controllers.append(fdcacontroller_settings)

        self.load_settings_done.emit()

    @staticmethod
    def _copy_dict(source, destination):
        for key, value in source.items():
            if isinstance(value, list):
                destination[key] = SteeringWheelControlSettings._copy_list(value)
            elif isinstance(value, dict):
                try:
                    destination[key]  # make sure that the destination dict has an entry at key
                except KeyError:
                    destination[key] = dict()
                SteeringWheelControlSettings._copy_dict(value, destination[key])
            elif hasattr(value, '__dict__') and not isinstance(value, Enum) and not inspect.isclass(value):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    destination[key] = value.as_dict()
                except NotImplementedError:
                    destination[key] = dict()
                    SteeringWheelControlSettings._copy_dict(value.__dict__, destination[key])
            else:
                destination[key] = source[key]

    @staticmethod
    def _copy_list(source):
        output_list = []
        for index, item in enumerate(source):
            if isinstance(item, list):
                output_list.append(SteeringWheelControlSettings._copy_list(item))
            elif hasattr(item, '__dict__') and not isinstance(item, Enum) and not inspect.isclass(item):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    output_list.append(item.as_dict())
                except NotImplementedError:
                    output_list.append(dict())
                    SteeringWheelControlSettings._copy_dict(item.__dict__, output_list[index])
            else:
                output_list.append(item)
        return output_list

    def remove_controller(self, setting):
        if isinstance(setting, PDControllerSettings):
            self.pd_controllers.remove(setting)

        if isinstance(setting, FDCAControllerSettings):
            self.fdca_controllers.remove(setting)


class PDControllerSettings:
    def __init__(self):
        # default controller values
        self.t_lookahead = 0.6
        self.k_p = 8.0
        self.k_d = 1.0
        self.w_lat = 1.0
        self.w_heading = 2.0
        self.trajectory_name = "default_hcr_trajectory.csv"

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class FDCAControllerSettings:
    def __init__(self):
        self.t_lookahead = 0.0
        self.k_y = 0.1
        self.k_psi = 0.4
        self.lohs = 1.0
        self.sohf = 1.0
        self.loha = 0.0
        self.trajectory_name = "default_hcr_trajectory.csv"

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)
