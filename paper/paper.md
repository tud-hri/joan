--- 
title: 'JOAN: a framework for human-automated vehicle interaction experiments in a virtual reality driving simulator' tags:

- Human-automated vehicle interaction
- Automated driving
- Human factors experiments
- Simulation
- Virtual Reality
- CARLA authors:
- name: Niek Beckers^[co-first author]
  orcid: 0000-0001-7077-9812 affiliation: 1
- name: Olger Siebinga^[co-first author]
  orcid: 0000-0002-5614-1262 affiliation: 1
- name: Joris Giltay affiliation: 1
- name: Andre van der Kraan affiliation: 1 affiliations:
    - name: Human-Robot Interaction group, Department of Cognitive Robotics, Faculty 3mE, Delft University of Technology, Mekelweg 2, 2628 CD Delft, The
      Netherlands index: 1 date: 28 Januari 2022 bibliography: paper.bib

--- 

# Summary

In the coming decades, traffic on the roads will no longer only consist of human traffic participants. Humans will have to share the road, and interact with,
autonomous vehicles (AVs). To design AVs that can safely handle such interactions, research into human-AV interaction is needed. This research can partly be
done in driving simulators. However, existing driving simulators are expensive, implementing new functionality (e.g., AV controllers)
can be difficult, and setting up new experiments can be tedious. To address these issues, we present JOAN, a framework for human-AV interaction experiments.
JOAN connects to the open-source AV-simulation program Carla and enables quick and easy implementation of simple driving experiments using a GUI. It supports
experiments in VR, a variety of human input devices, and haptic feedback. JOAN is easy to use, flexible, and enables researchers to perform simple experiments
without writing a single line of code.

# Statement of need

Real-world traffic is rapidly changing, since a few years, (partly) automated vehicles (AVs) are driving among other road users. It is likely that traffic will
be mixed for the coming decades, with manually driven vehicles, vehicles of various levels of automation, and vulnerable road users (e.g., pedestrians and
cyclists) sharing the same road [@di2020_survey]. Therefore, investigating the interaction between AVs and humans is critical for the development of safe and
acceptable AV behavior. Driving simulators are invaluable tools to study such human-AV interactions.

State-of-the-art driving simulators use motion platforms, immersive graphics [@wivw-scilab], and/or high-fidelity haptic feedback [@mulder2012_sharing] to
create simulations with high levels of realism [@slob2008_stateoftheart]. However, such simulators require dedicated (and expensive)
hardware, limiting their availability. Furthermore, they require a steep programming learning curve and lack the flexibility to quickly implement customized
experiments.

As an alternative, virtual-reality-based driving simulators offer reasonable levels of realism, require relatively low-cost hardware, and are generally more
flexible in terms of new implementations. For example, Bazilinskyy et al. [@bazilinskyy2020_coupled] and Kearney et al. [@kearney2018_multimodal] developed  
simulators based on the Unity game engine. Both simulators are specifically developed for human-human interaction, they lack the framework to implement AV
driving models, which is necessary to simulate mixed-traffic scenarios.

On the other hand, there are several game engine-based simulators, designed specifically for the development of AVs (e.g., @airsim2017fsr, @lgsvlsim, and
@dosovitskiy2017_carla). These simulators do not support human-in-the-loop experiments but do provide possibilities for implementing, training, and validating
fully automated driving. One of the popular open-source simulators is CARLA (based on the Unreal-Engine); it provides a flexible and well-documented API,
pre-trained automated driving models, common roadmap standards (OpenDrive), and is actively maintained.

Silvera et al. extended Carla to support human-in-the-loop experiments [@Silvera2022]. They created an affordable driving simulator that can be used for
human-AV interaction experiments which leverages the benefits of CARLA (for AV development). However, their software is restricted to specific hardware (both
for human input and VR), and requires extensive programming to implement customized experiments because it lacks a general experiment framework.

To address these issues, we introduce JOAN, an open-source framework for conducting human-in-the-loop driving experiments. JOAN interfaces with Carla, is
written in Python, and can be fully controlled with a GUI. JOAN can be used with a variety of human input devices, among which game console controller (e.g.,
Xbox or PlayStation), a SensoDrive steering wheel [@sensodrive] (for including haptic feedback), or generic USB controllers (e.g., Logitech G920). JOAN includes
a framework for experiment design to create and execute experiments, and provides reliable data acquisition. These features can be accessed through a
user-friendly interface, which means no extensive (knowledge of) programming nor a lot of time is required to set up new experiments.

For detailed instructions on how to install and use JOAN, see our online documentation[^1]. JOAN can be found in a
GitLab repository[^2], a video with more information can be found on
YouTube[^3].

[^1]: https://joan.readthedocs.io
[^2]: https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan
[^3]: https://www.youtube.com/watch?v=TLLw48isYJU
# Software functionality

We set the following requirements for JOAN based on the needs of a typical human-in-the-loop driving experiment. JOAN should:

- provide reliable data acquisition,
- enable researchers to connect multiple types of user input devices,
- facilitate the design and execution of experiment protocols; create repeatable traffic scenarios involving multiple agents,
- provide an easy way to design experiments by providing access to most functionality from a GUI
- be flexible and extensible by design, and
- include support for haptic feedback.

To address the flexibility and extensibility requirements, JOAN consists of modules, each module with its specific purpose. These modules can be enabled 
or disabled based on the needs of a researcher, if needed they can easily be adapted or extended, and researchers
can create new modules to implement new functionality in JOAN. The standard modules included with JOAN can:

- log and plot experiment data,
- handle hardware inputs,
- provide a human with haptic feedback,
- design and execute experiments with multiple conditions, and
- implement traffic scenarios with dynamic triggers for events.

Each module has its own GUI which appears if the module is enabled. These dialogs provide access to all standard functionality of the module. A researcher can
design and perform a simple human-in-the-loop experiment without writing a single line of code. The documentation provides more information for researchers who
want to extend current modules (e.g. for other hardware inputs), or who want to write a new module (e.g. to implement specific controllers).

# Usage in Science and Education

A core research focus of our department is the haptic interaction between human drivers and their vehicles (e.g., @abbink2018_topology, @mulder2012_sharing).
Therefore, JOAN provides support for a haptic force-feedback steering wheel. The \textbf{SteeringWheelController} module enables implementation of control
algorithms for force feedback and comes with two example implementations: a standard PD controller [@mulder2012_sharing] and a Four Design Choice Architecture
controller (FDCA) [@vanpaassen2017_four] (for quick-start haptic feedback experiments).

JOAN was used in several human-in-the-loop experiments (for a published example, see [@Melman2021]), many were executed by master students for
their thesis. This illustrates that JOAN provides a framework that is flexible and quick to implement (Master thesis projects are completed in 6 months).
Therefore, we believe that JOAN is a valuable driving simulator for use in both education and research.

# Acknowledgements

This work was supported by the VIDI grant `Symbiotic Driving' awarded to D.A. Abbink (NWO-TTW) and AiTech at the TU Delft. We thank Timo, Cedric, Sam, Peter,
Mark, and Tarbiya for their support in the initial stages of software development.

# References