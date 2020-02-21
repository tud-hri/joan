# SharedControlDrivingSim

A start to combine classes in a lego-like way to make a driving simulator.<br>
Inspired by mis-haptic-trainer
<br><br>
Editor:<br>
Visual Studio Code
<br><br>
Software:<br>
Use PyQt5 and NOT PySide2 because PyQt5 is (more) platform independent.<br>
* PyQt5-5.13.2<br>
* Python 3.8.1 64-bit<br>
<br>
<br>
## hapticsimulator

* haptictrainer.py (1 instance of HapticTrainer class) 
* states.py (State class, 1 instance of States class)
* statehandler.py
<br>
## signals
* pulsar.py (very early stage)<br>
purpose is to have 2 threads, beside the main process, one for the polling of signals (hopefully 1 msec) and one for spread data around (200msec or so)