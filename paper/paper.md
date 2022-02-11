--- 
title: 'JOAN: a framework for human-automated vehicle interaction experiments in a virtual reality driving simulator' 
tags:
  - Human-automated vehicle interaction
  - Automated driving
  - Human factors experiments
  - Simulation
  - Virtual Reality
  - CARLA 
authors:
  - name: Niek Beckers^[co-first author]
    orcid: 0000-0001-7077-9812 
    affiliation: 1
  - name: Olger Siebinga^[co-first author]
    orcid: 0000-0002-5614-1262 
    affiliation: 1
  - name: Joris Giltay 
    affiliation: 1
  - name: André van der Kraan 
    affiliation: 1 
affiliations:
  - name: Human-Robot Interaction group, Department of Cognitive Robotics, Faculty 3mE, Delft University of Technology, Mekelweg 2, 2628 CD Delft, The Netherlands 
    index: 1 
date: 7 February 2022 
bibliography: paper.bib
--- 

# Summary

With the rapid development of automated driving systems, human drivers will soon have to share the road, and interact with, autonomous vehicles (AVs). To design AVs that can be safely introduced in our mixed traffic, research into human-AV interaction is needed. Driving simulators are invaluable tools, however, existing driving simulators are expensive, implementing new functionalities (e.g., AV control algorithms) can be difficult, and setting up new experiments can be tedious. To address these issues, we present JOAN, a framework for human-AV interaction experiments. JOAN connects to the open-source AV-simulation program Carla and enables quick and easy implementation of simple driving experiments. It supports experiments in VR, a variety of human input devices, and haptic feedback. JOAN is easy to use, flexible, and enables researchers to design, store, and perform human-factors experiments without writing a single line of code.


# Statement of need

Real-world traffic is rapidly changing: automated vehicles, even autonomous vehicles, are rapidly being introduced on the roads interacting with other road users. It is likely that traffic will be mixed for the coming decades, with manually driven vehicles, vehicles of various levels of automation, and vulnerable road users (e.g., pedestrians and cyclists) sharing the same road [@di2020_survey]. Therefore, investigating the interaction between AVs and other road users is critical for the development of safe and acceptable AV behavior. Driving simulators are invaluable tools to study such human-AV interactions.

State-of-the-art driving simulators use motion platforms, immersive graphics [@wivw-scilab], and/or high-fidelity haptic feedback [@mulder2012_sharing] to create simulations with high levels of realism [@slob2008_stateoftheart]. However, such simulators require dedicated and often expensive hardware, limiting their availability for algorithm development and evaluation. Furthermore, they require a steep programming learning curve and lack the flexibility to quickly implement customized experiments.

Alternatively, virtual-reality-based driving simulators offer reasonable levels of realism, require relatively low-cost hardware, and are generally more
flexible in terms of rapid algorithm development or experiment evaluation. Traffic simulators based on the Unity game engine have been developed for studying human-human interaction in mixed traffic [@bazilinskyy2020_coupled; @kearney2018_multimodal]. However, both lack the framework to implement AV driving models, which is necessary to simulate mixed-traffic scenarios.

Several game engine-based simulators exist that only specifically focus on AV algorithm development  (e.g., [@airsim2017fsr; @lgsvlsim;
@dosovitskiy2017_carla]). While such simulators provide possibilities for implementing, training, and evaluating fully automated driving algorithm, they do not support human-in-the-loop experiments. A popular open-source simulators is CARLA (based on the Unreal-Engine); it provides a flexible and well-documented API,
pre-trained automated driving models, common roadmap standards (OpenDrive), and is actively maintained.

Silvera et al. extended Carla to support human-in-the-loop experiments [@Silvera2022]. They created an affordable driving simulator primarily implemented in C++ and python that can be used for human-AV interaction experiments which leverages the benefits of CARLA for AV development. However, because their software is not set up with a more general experiment framework that allows customizability, their software is restricted to specific hardware (both for human input and VR headsets) and requires extensive programming to implement customized experiments.

To address these issues, we created JOAN, an open-source framework for conducting human-in-the-loop driving experiments. JOAN interfaces with Carla, is
written in Python, is fully customizable through code and graphical user interfaces (GUI). JOAN can be used with a variety of human input devices, including game console controllers (e.g.,Xbox or PlayStation), generic USB controllers (e.g., Logitech G920), or a SensoDrive high-fidelity steering wheel [@sensodrive] (for including haptic feedback). JOAN includes a framework for experiment design to create and execute experiments, and provides reliable data acquisition. These features can be accessed through a user-friendly interface, which means no extensive (knowledge of) programming nor a lot of time is required to set up new experiments.

For detailed instructions on how to install and use JOAN, see our online documentation[^1]. JOAN can be found in a GitLab repository[^2], a video with more information can be found on YouTube[^3].

[^1]: https://joan.readthedocs.io
[^2]: https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan
[^3]: https://www.youtube.com/watch?v=TLLw48isYJU

# Software functionality

We set the following requirements for JOAN based on the needs of a typical human-in-the-loop driving experiment. JOAN should:

- provide reliable data acquisition,
- enable researchers to connect multiple types of user input devices,
- facilitate the design and execution of experiment protocols; create repeatable traffic scenarios involving multiple agents,
- provide an easy way to design experiments by providing access to most functionality from a GUI,
- be flexible and extensible by design, and
- include support for haptic feedback.

JOAN consists of modules, each with a functionality, to address the flexibility and extensibility requirements. These modules can be enabled or disabled based on the needs of a researcher, if needed they can easily be adapted, and researchers can create new modules to implement new functionality. The standard modules included with JOAN:

- log and plot experiment data,
- handle hardware inputs,
- design and execute experiments with multiple conditions,
- implement traffic scenarios with dynamic triggers for events,
- provide a human with haptic feedback.

Each module has its own GUI which appears if the module is enabled. These interfaces provide access to all standard functionality of the module. A researcher can
design and perform a simple human-in-the-loop experiment without writing a single line of code. The documentation provides more information for researchers who
want to adapt existing modules (e.g. to implement new hardware), or who want to write a new module (e.g. to implement specific controllers).

# Usage in Science and Education

JOAN was used to quickly develop and perform several human-in-the-loop experiments (including various MSc students, for a published example, see [@Melman2021]), illustrating that
JOAN provides a framework that is flexible and quick to implement (most projects are completed in 6 months). Furthermore, a core research focus of our department is the haptic
interaction between human drivers and their vehicles (e.g., [@abbink2018_topology; @mulder2012_sharing]), for which we implemented a module to control a haptic force-feedback
steering wheel. The `SteeringWheelController` module enables implementation of control algorithms for force feedback and comes with two example implementations: a standard PD
controller [@mulder2012_sharing] and a Four Design Choice Architecture controller (FDCA) [@vanpaassen2017_four].

# Acknowledgements

We thank Timo, Cedric, Sam, Peter, Mark, and Tarbiya for their support in the initial stages of software development.

# References