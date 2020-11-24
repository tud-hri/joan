import math

from core.module_process import ModuleProcess
from modules.datarecorder.datarecorder_settings import DataRecorderSettings
from modules.joanmodules import JOANModules


class DataRecorderProcess(ModuleProcess):
    settings: DataRecorderSettings

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)
        self.settings = settings
        self.news = news

        self.variables_to_be_saved = {}
        self.save_path = ''
        self.trajectory_save_path = ''

        self.file = None
        self.trajectory_file = None
        self.index = 0
        self.temp = [0,0]
        self.travelled_distance = 0

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings are converted to type dict
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        self.variables_to_be_saved = self.settings.variables_to_be_saved
        self.save_path = self.settings.path_to_save_file

        if self.settings.should_record_trajectory:
            self.trajectory_save_path = self.settings.path_to_trajectory_save_file
            try:
                self.carla_interface_variables = self.news.read_news(JOANModules.CARLA_INTERFACE)
                self.transform = self.carla_interface_variables.agents['Ego Vehicle_1'].transform
                self.trajectory_file = open(self.trajectory_save_path, 'w')
            except Exception as inst:
                print(inst)

        header = ', '.join(['.'.join(v) for v in self.variables_to_be_saved])
        with open(self.save_path, 'w') as self.file:
            self.file.write(header + '\n')

    def _run_loop(self):
        with open(self.save_path, 'a') as self.file:
            if self.settings.should_record_trajectory == True:
                with open(self.trajectory_save_path, 'a') as self.trajectory_file:
                    super()._run_loop()
            else:
                super()._run_loop()


    def do_while_running(self):
        """
        do_while_running something and, for datarecorder, read the result from a shared_variable
        """
        row = self._get_data_row()
        self.file.write(row + '\n')

        if self.settings.should_record_trajectory == True:
            self._write_trajectory_row()


    def _get_data_row(self):
        row = []
        for variable in self.variables_to_be_saved:
            module = JOANModules.from_string_representation(variable[0])
            last_object = self.news.read_news(module)

            for attribute_name in variable[1:]:
                if isinstance(last_object, dict):
                    last_object = last_object[attribute_name]
                elif isinstance(last_object, list):
                    last_object = last_object[int(attribute_name)]
                else:
                    last_object = getattr(last_object, attribute_name)

            row.append(str(last_object))

        return ', '.join(row)

    def _write_trajectory_row(self):
        try:
            self.transform = self.carla_interface_variables.agents['Ego Vehicle_1'].transform
            velocities = self.carla_interface_variables.agents['Ego Vehicle_1'].velocities
            applied_inputs = self.carla_interface_variables.agents['Ego Vehicle_1'].applied_input

            travelled_distance_tick_x = self.transform[0] - self.temp[0]
            travelled_distance_tick_y = self.transform[1] - self.temp[1]
            travelled_distance_tick = math.sqrt(travelled_distance_tick_x**2 + travelled_distance_tick_y**2)
            self.travelled_distance += travelled_distance_tick


            if self.travelled_distance > 0.0:
                self.index += 1
                trajectory_row = [self.index, self.transform[0], self.transform[1], applied_inputs[0], applied_inputs[4], applied_inputs[3], self.transform[3],
                                  math.sqrt(velocities[0] ** 2 + velocities[1] ** 2 + velocities[2] ** 2)]

                self.trajectory_file.write(", ".join(repr(e) for e in trajectory_row) + '\n')
                self.travelled_distance = 0.0

            self.temp = [self.transform[0], self.transform[1]]
        except Exception as inst:  # this would mean there is no ego_vehicle to record trajectory for
            print(inst)