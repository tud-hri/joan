# JOAN

[![Documentation](https://readthedocs.org/projects/joan/badge/?version=latest)](http://joan.readthedocs.io)

# Introduction

To design automated vehicles (AVs) that can be safely introduced in our mixed traffic, research into human-AV interaction is needed. Driving simulators are invaluable tools, however, existing driving simulators are expensive, implementing new functionalities (e.g., AV control algorithms) can be difficult, and setting up new experiments can be tedious. To address these issues, we present JOAN, a framework for human-AV interaction experiments. JOAN connects to the open-source AV-simulation program Carla and enables quick and easy implementation of human-in-the-loop driving experiments. It supports experiments in VR, a variety of human input devices, and haptic feedback. JOAN is easy to use, flexible, and enables researchers to design, store, and perform human-factors experiments without writing a single line of code.

JOAN builts upon Carla, a open-source game-based driving simulation created to develop AV algorithms. Carla provides a flexible and well-documented API, pre-trained automated driving models, common roadmap standards (OpenDrive), and is actively maintained. While Carla provides possibilities for implementing, training, and evaluating fully automated driving algorithm, it does not explicitly support human-in-the-loop experiments, or make it easy to set up or create such experiments. Carla requires the user to create their own code to use human interfaces, which can be challenging and time-consuming depending on the experimenter's coding abilities.

To address these issues, we created JOAN, an open-source framework for conducting human-in-the-loop driving experiments. JOAN interfaces with Carla, is written in Python, and is fully customizable through code and graphical user interfaces (GUI). JOAN can be used with a variety of human input devices, including game console controllers (e.g.,Xbox or PlayStation), generic USB controllers (e.g., Logitech G920), or a SensoDrive high-fidelity steering wheel (for including haptic feedback). JOAN includes a framework for experiment design to create and execute experiments, and provides reliable data acquisition. These features can be accessed through a user-friendly interface, which means no extensive (knowledge of) programming nor a lot of time is required to set up new experiments.

JOAN mainly consists of modules, which communicate with each other through a News channel. The main modules are:

- CARLA interface
- Hardware Manager
- Data recorder
- Data Plotter
- Experiment Manager
- Haptic Controller Manager

See [JOAN overview](docs/firststeps-joan-overview.md) for more information, or read the module-specific documentation.

This documentation will help you in setting up CARLA and JOAN, guide you through your first steps, and provide more in depth information in how JOAN works and how you can tweak it to your preferences (which is highly encouraged!).

Have fun!

## Documentation

For the most up-to-date documentation, visit [https://joan.readthedocs.io/en/latest/](https://joan.readthedocs.io/en/latest/).

## Licensing and reference

JOAN is developed by a team (Joris, Olger, Andre, and Niek -> JOAN) of the Human-Robot Interaction group of Cognitive Robotics at Delft University of Technology.


Please see our license if you want to use our framework.

Please use the following citation:
> Beckers, N., Siebinga, O., Giltay, J., & Van der Kraan, A. (2021). JOAN, a human-automated vehicle experiment framework. Retrieved from https://github.com/tud-hri/joan

