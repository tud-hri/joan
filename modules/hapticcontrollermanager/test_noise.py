import numpy as np
import matplotlib.pyplot as plt
import math



def hfn(t, v):
    freqs = [0.5, 1, 3, 7, 15, 24, 35, 40, 56, 70, 100, 150, 230, 350, 600, 1200, 1800]
    phases = [1, -2, 3, -4, 1.7, -1.2, 1.92, -2.34, -1.32, -0.23, -0.25, 5, -4, 0.98, 2.2, -4, 3.5, -6, -1]
    amp = [0.4, 0.48, 0.5, 0.54, 0.58, 0.68, 0.79, 0.8, 0.95, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    factor = 0.001
    n = len(freqs)
    noise = 0
    v0 = 30
    fac = (v0 + v) / v0
    for i in range(n):
        noise += factor * amp[i] * math.sin(fac * freqs[i] * 2 * np.pi * t + phases[i])
        # print(noise)
    return noise

noise = [0]
t=[0]
for i in range(1000):
    t.append(t[-1] + 0.01)
    noise.append(hfn(t[-1]))


plt.plot(t, noise)
plt.show()