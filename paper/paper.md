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
- name: Andre van der Kraan 
  affiliation: 1 
affiliations:
  - name: Human-Robot Interaction group, Department of Cognitive Robotics, Faculty 3mE, Delft University of Technology, Mekelweg 2, 2628 CD Delft, The Netherlands
  index: 1 
date: 05 August 2021 
bibliography: paper.bib
--- 

# Summary

# Statement of need

The traffic scene is rapidly changing; vehicles with increasing levels of automation are emerging on the roads interacting with other road users. It is likely that traffic will be mixed in the future, with manually driven vehicles, automated vehicles in various automation levels, and vulnerable road users such as pedestrians and cyclists sharing the road [@di2020_survey]. Hence, investigating human behavior in understanding how humans interact with automated vehicles (AVs) and using this knowledge develop better technology remain major challenges, which requires extensive human factors and human-AV interaction research. Driving simulators are invaluable tools to study such human-AV interactions. They enable researchers to create repeatable test scenarios that may not be practical to implement in the real world, for example, due to safety concerns. Furthermore, they allow us to test human-AV interaction algorithms (on human behavior) before they are deployed.

State-of-the-art driving simulators for studying human behavior are able to create driving scenarios with high levels of realism [@slob2008_stateoftheart]. For example, driving simulators use motion platforms, immersive graphics, are able to simulate realistic traffic scenarios [@wivw-scilab], or have high fidelity haptic feedback on the steering wheel and pedals [@mulder2012_sharing]. However, such driving simulators require dedicated (and expensive) hardware, possibly limiting their availability, Furthermore, they require a steep programming learning curve, or lack the support or flexibility to quickly implement customized experiments.

Virtual reality driving simulators based on video game platforms offer reasonable levels of realism, require relatively low-cost hardware, and are able to simulate complex traffic scenarios involving multiple actors. Bazilinskyy et al. [@bazilinskyy2020_coupled] developed an open-source virtual reality simulator for investigating interactions in traffic scenarios based on the Unity game engine. Their simulator supports human user input from different types of hardware interfaces, such as USB steering wheels or motion capture suits. Similarly, Kearney et al. [@kearney2018_multimodal] also developed a Unity-based driving simulator in which multiple human participants can be coupled in the same simulator environment. These simulators are specifically developed for human-human interaction experiments and can simulate human-AV interactions by having a human pretending to be an AV (`Wizard of Oz' experiment), but they lack the framework to implement automated vehicle driving models, which is necessary to simulate complex multi-actor mixed traffic scenarios.

Several game engine-based reality driving simulators have been developed specifically for the development of fully automated driving models. Examples include AirSim [@airsim2017fsr], LGSVL simulator [@lgsvlsim], and CARLA [@dosovitskiy2017_carla]. These simulators provide support for implementing, training, and validating fully automated driving models and are able to simulate various traffic scenarios, ranging from a single automated vehicle driving around a country road to complex scenarios involving multiple automated vehicles and other road users. CARLA is a popular open-source simulator; it provides a flexible and well-documented API, pre-trained automated driving models, supports common roadmap standards such as OpenDrive, is actively maintained and further developed, and has an active community. CARLA uses the Unreal Engine, which handles the physics simulation and rendering, supports virtual reality goggles, and enables the user to easily create realistic virtual environments. Because CARLA is specifically built for simulating complex multi-agent traffic scenarios, it provides human factors researchers with a flexible and extensible platform for investigating human behavior in complex multi-actor traffic scenarios. However, CARLA currently does not provide support for human-in-the-loop experiments.

Here, we introduce JOAN, an open-source framework for studying human behavior in traffic scenarios using the CARLA driving simulator. JOAN is programmed in Python with cross-platform compatibility in mind. Setting up a human-in-the-loop experiment requires a number of programming steps, including (1) communicating with the CARLA simulator, (2) connecting user input devices (such as steering wheels), (3) providing a framework for experiment design to create and execute experiments, and (4) providing reliable data acquisition. JOAN facilitates this process, provides a user-friendly interface, and reduces the time required to set up new human-AV interaction experiments in CARLA. Here we present an overview of the software framework, including a discussion of the core components of JOAN, and an illustrative example. For detailed documentation on how to install, use and program JOAN, see our online documentation\footnote{\url{https://joan.readthedocs.io}} The code is open-source (GPL license) and maintained in a GitLab repository\footnote{\url{https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan}}.

# Software functionality
JOAN was developed to combine the potential of an existing simulation environment for autonomous vehicles (the CARLA simulator) with human driver inputs in scientific experiments. We set the following requirements for JOAN based on the needs of a typical human-in-the-loop driving experiment:

- Provide reliable data acquisition
- Enable researchers to connect multiple types of user input devices (steering wheels, etc.) with agents in CARLA
- Facilitate the design and execution of experiment protocols; allow researchers to create repeatable traffic scenarios involving multiple agents (humans, 
  AVs, etc.) in CARLA
- Provide an easy way to design simple experiments by providing access to most functionality from a graphical user interface
- Be flexible and extensible by design, to support customization both within current functionality and for new functionality
- Include support for haptic feedback on a haptic steering wheel to study haptic human-AV interaction

To address the flexibility and extensibility requirements, JOAN is designed as a set of modules. Each module inherits from abstract base classes and has its own specific purpose. These modules can be added or removed based on the needs of a researcher, if needed they can easily be adapted or extended, and researchers can create their own modules to implement new functionality in JOAN. The standard modules included with JOAN can: log and plot experiment data, handle hardware inputs, design and execute experiments with multiple conditions, implement traffic scenarios with dynamic triggers for events and provide a human with haptic feedback.

Each module has its own graphical user interface dialog which appears in the JOAN main menu if the module is being used. These dialogs provide access to all standard functionality of the modules. A researcher can design and perform a simple human-in-the-loop experiment without writing a single line of code. The documentation provides more information for researchers who want to extend current modules e.g. to create their own hardware input for custom setups, or who want to write new module e.g. to implement specific vehicle controllers or other forms of feedback to the human.

# Usage in Science and Education

A core research focus of our department is on haptic interaction between human drivers and their automated vehicles, mainly through haptic interaction torques on the steering wheel (see [@abbink2018_topology], [@mulder2012_sharing]). We, therefore, enabled users to connect a haptic force-feedback steering wheel to JOAN, which is able to generate feedback torques based on the state of the vehicle (e.g., position on the road, velocity), the state of the driver, and the environment (e.g., road, obstacles, other road users, etc.). We created the \textbf{SteeringWheelController} module in which users are able to implement the controller algorithms for calculating these torques (\ref{req:hscsupport}). We provide two controllers: a standard PD controller (used by [@mulder2012_sharing]) and a Four Design Choice Architecture controller (FDCA, see [@vanpaassen2017_four]). The torques are sent to the haptic feedback steering wheel through the HardwareManager (i.e. the HardwareManager reads the desired torque through News of SteeringWheelController, and sends it to the steering wheel).

JOAN is tested in a number of human-in-the-loop experiments. Fig.~\ref{fig:screenshots-example} shows screenshots of JOAN and CARLA in a typical human-in-the-loop experiment. We provide a more complete overview of JOAN in combination with CARLA in a video (\url{https://www.youtube.com/watch?time_continue=278&v=TLLw48isYJU&feature=emb_logo}).

# Acknowledgements

This work was supported by the VIDI grant `Symbiotic Driving' awarded to D.A. Abbink (NWO-TTW) and AiTech at the TU Delft. We thank Cedric, Sam, Peter, Mark, Tarbiya for their support in the initial stages of software development.

# References