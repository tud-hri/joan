# Introduction

To design automated vehicles (AVs) that can be safely introduced into our mixed traffic, research into human-AV interaction is needed. Driving simulators are invaluable tools, however, existing driving simulators are expensive, implementing new functionalities (e.g., AV control algorithms) can be difficult, and setting up new experiments can be tedious. To address these issues, we present JOAN, a framework for human-AV interaction experiments. JOAN connects to the open-source AV-simulation program Carla and enables quick and easy implementation of human-in-the-loop driving experiments. It supports experiments in VR, a variety of human input devices, and haptic feedback. JOAN is easy to use, flexible, and enables researchers to design, store, and perform human-factors experiments without writing a single line of code.

JOAN builds upon Carla, an open-source game-based driving simulation created to develop AV algorithms. Carla provides a flexible and well-documented API, pre-trained automated driving models, common roadmap standards (OpenDrive), and is actively maintained. While Carla provides possibilities for implementing, training, and evaluating fully automated driving algorithms, it does not explicitly support human-in-the-loop experiments, nor makes it easy to implement such experiments. Carla requires the user to create their own code to use human interfaces, which can be challenging and time-consuming depending on the experimenter's coding abilities.

Besides the lack of standardized methods to interface with human input devices, Carla was not designed for repeatable human-in-the-loop experiments. There is no possibility to automatically reset specific scenarios. Nor is there a way to create an experiment with multiple (slightly distinct) conditions. There is also no central data recorder that can easily store data from both the Carla side and from human input devices. 

To address these issues, we created JOAN, an open-source framework for conducting human-in-the-loop driving experiments. JOAN interfaces with Carla, is written in Python, and is fully customizable through code and graphical user interfaces (GUI). JOAN can be used with a variety of human input devices, including game console controllers (e.g., Xbox or PlayStation), generic USB controllers (e.g., Logitech G920), or a SensoDrive high-fidelity steering wheel (for including haptic feedback). JOAN includes a framework for experiment design to create and execute experiments, and provides reliable data acquisition. These features can be accessed through a user-friendly interface, which means no extensive (knowledge of) programming nor a lot of time is required to set up new experiments.

JOAN is composed of modules, which communicate with each other through a News channel. All modules have a Settings class which can alter the experiment. The main difference between News and Settings is that News is constantly updated during an experiment Trial while Settings remain constant over a trial. All modules run in their own Python process, meaning that they run completely parallel. The main modules in JOAN are:

- __CARLA interface__
The Carla interface module communicates with Carla. Vehicles (both human driver and NPC) can be spawned from here. It is also the module that connects certain inputs (human inputs or NPC controllers) to specific vehicles 

- __Hardware Manager__
The hardware manager is used to connect human input devices to JOAN. This is where raw input (e.g., a USB joystick axis value) is translated to a vehicle command (e.g., brake level).

- __Data recorder__
The data recorder is used to store experimental data in CSV files. It automatically recognizes all variables shared in the News classes of all active modules. Even if you add your own new module. If you want to store a variable during your experiment, all you have to do is add it to the News class of the corresponding module. It will then become available to store in the data recorder’s GUI.  

- __Data Plotter__
The data plotter works in the same way as the data recorder, just select a variable from the News class of a specific module, and it will be plotted. This module was created for debugging convenience, if you want to store plots, we recommend you save the raw data instead and create your own plot afterward.  

- __Experiment Manager__
The Experiment manager can be used to store and load the settings of all modules in JOAN. It can therefore reset the whole state of JOAN to a specific condition. Experiments are saved as a set of base settings with conditions saved as the deviations from the base settings. This is all saved in human-readable JSON files. If you want to manipulate a variable in your experimental conditions, all you have to do is add that variable to the modules Settings (even for your own new modules).   

- __Haptic Controller Manager__
The Haptics Controller Manager calculates the haptics feedback for the steering wheel. It is a separate module and can therefore run in parallel with the other modules, this ensures haptics feedback will not stutter if other modules are under heavy load. 

- __NPC Controller Manager__
The NPC (non-playable character) controller manager holds controllers that can drive NPC (or other traffic) vehicles.  

See [JOAN overview](firststeps-joan-overview.md) for more information, or read the module-specific documentation.

This documentation will help you in setting up CARLA and JOAN, guide you through your first steps, and provide more in-depth information on how JOAN works and how you can tweak it to your preferences (which is highly encouraged!). An applied example of how JOAN can be used for science can be found in [Melman et al. 2021](https://doi.org/10.1155/2021/4396401).

Have fun!

