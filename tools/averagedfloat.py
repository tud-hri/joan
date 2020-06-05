class AveragedFloat:
    """
    This object can be used as a float value with a build in discrete moving average filter applied. When initialized the number of samples can be set.
    All samples are initialized with the initial value. The default values for the number of samples and initial value are 100 and 0.0.

    To use the filtered value AveragedFloat.value should be set and used.

    Example:
        filtered_sensor_value = AveragedFloat(samples=60, initial_value=15.0)

        while True:
            measured_sensor_value = sensor.get_input()
            filtered_sensor_value.value = measured_sensor_value

            do_calculation(filtered_sensor_value.value)

    """

    def __init__(self, samples: int = 100, initial_value: float = 0.0):
        self._values = [float(initial_value)] * int(samples)

    def __str__(self):
        return str(self.value)

    @property
    def value(self):
        return sum(self._values) / float(len(self._values))

    @value.setter
    def value(self, val: float):
        self._values.append(float(val))
        self._values.pop(0)
