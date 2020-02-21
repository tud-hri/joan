# SharedControlDrivingSim

A start to combine classes in a lego-like way to make a driving simulator.<br>
Inspired by mis-haptic-trainer
<br>
Editor:
Visual Studio Code

Software:
Use PyQt5 and NOT PySide2 because PyQt5 is (more) platform independent.
PyQt5-5.13.2
Python 3.8.1 64-bit


<br>
## Hapticsimulator
 - haptictrainer.py (1 instance of HapticTrainer class) 
 - states.py (State class, 1 instance of States class)
 - statehandler.py

## signals
- pulsar.py (very early stage)
purpose is to have 2 threads, one for the polling of signals (hopefully 1 msec) and one for spread data around (200msec or so)