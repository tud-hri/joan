import numpy as np

class LowPassFilterBiquad:
    def __init__(self, fs, fc, q=0.5 * np.sqrt(2), x0=None, y0=None):
        """
        Initialize, calculate the filter coefficients for a second-order low-pass filter
        :param fs: sampling frequency (Hz)
        :param fc: corner frequency (Hz)
        :param q: quality factor, use 0.5*sqrt(2) for butterworth filter
        """

        w0 = 2 * np.pi * (fc / fs)
        alpha = np.sin(w0) / (2 * q)

        self.a0 = 1 + alpha
        self.a1 = (-2 * np.cos(w0)) / self.a0
        self.a2 = (1 - alpha) / self.a0


        self.b0 = ((1 - np.cos(w0)) / 2 )/ self.a0
        self.b1 = ((1 - np.cos(w0)) ) / self.a0
        self.b2 = ((1 - np.cos(w0)) / 2) / self.a0

        self.a0 = self.a0 / self.a0



        print("a:" ,self.a0, self.a1, self.a2)
        print("b:" ,self.b0, self.b1, self.b2)

        # initial conditions
        if y0 is None:
            y0 = [0.0, 0.0]
        if x0 is None:
            x0 = [0.0, 0.0]

        self.x = x0
        self.y = y0



    def step(self, x0: float):
        """
        Perform a filter step.
        Needs to be done at the sampling rate fs!!
        :param x: input, raw value
        :return: y: output, filtered value
        """
        # difference equation
        y0 = (1.0 / self.a0) * (self.b0 * x0 + self.b1 * self.x[0] + self.b2 * self.x[1] - self.a1 * self.y[0] - self.a2 * self.y[1])


        self.y[1] = self.y[0]
        self.y[0] = y0
        self.x[1] = self.x[0]
        self.x[0] = x0

        return float(y0)
