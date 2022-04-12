# JOAN documentation

Welcome to the JOAN human-automated vehicle interaction simulator documentation! This documentation should get you up and running with JOAN and [CARLA](http://carla.org){target="_blank"}.

JOAN is an open-source software framework that builds upon CARLA, a simulator made to study automated driving, by making CARLA also useful for human-in-the-loop experiments of human drivers and other road users interacting with automated vehicles. 

Among others, we build JOAN to enable you to

- quickly set up (human-in-the-loop) experiments with repeatable conditions
- define repeatable traffic scenarios
- easily log data
- implement haptic driver-automated vehicle interaction

Check out the table of content below for installation instructions and more information on JOAN. Also check out the [repository][repolink]{target="_blank"} for current issues, etc.

!!! Note 
    We tested JOAN with CARLA 0.9.9, not (yet) with the latest version. If you tested JOAN with the latest CARLA build (and it works), awesome! Please let us know through the
issue tracker!
    
---

JOAN is developed by members of the [Human-Robot Interaction group](https://delfthapticslab.nl){target="_blank"} at Cognitive Robotics of Delft University of Technology.

Please use the following reference if you end up using JOAN for your work (and do not forget to reference CARLA too!)

> Beckers, N., Siebinga, O., Giltay, J., & Van der Kraan, A. (2021). JOAN, a human-automated vehicle experiment framework. Retrieved from https://github.com/tud-hri/joan

---

We created a video showcasing JOAN and CARLA for the Symbiotic Driving Simulator for one of our research projects on haptic shared control in driving:

<iframe width="560" height="315" src="https://www.youtube.com/embed/xcGXE7rI61s" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

--- 

### Useful links

- Because JOAN depends heavily on CARLA, we strongly recommend you to check out the [CARLA documentation](https://carla.readthedocs.io/en/0.9.9/){target="_blank"}.
- You can find the JOAN repository [here][repolink]{target="_blank"}. The underlying framework of JOAN is finished, so that core functionality will not change to ensure backward
  compatibility.

[repolink]: https://github.com/tud-hri/joan

--- 

## Table of content

### Setup JOAN and CARLA
A thorough guide on setting up JOAN and CARLA:

* __[Setting up CARLA on Windows](setup-carla-windows.md)__ - The most important steps from the CARLA documentation
* __[Setting up JOAN](setup-joan.md)__ -- Install JOAN
* __[Setup JOAN on a TUD computer](setup-on-tud-shared-hardware.md)__ - a guide on how to install your project on TUD shared hardware (probably your first step)
* __[Example usage and testing](example-usage-and-testing.md)__ - example of JOAN usage and test whether everything works

### First steps
If you want to build up an understanding of JOAN the sections below are a good place to start:

* __[JOAN Overview](firststeps-joan-overview.md)__ - Core, Modules, Dataflow
* __[Quick Start Running Joan and CARLA](firststeps-joan-run.md)__ - Quickstart on how to run JOAN and CARLA
* __[Quick start CARLA environment](firststeps-carle-ue4.md)__ - Quickstart on CARLA and the Unreal Editor

### Using the JOAN modules
Several modules are included with JOAN by default, the way to use them is described in their separate sections:

!!! Important
    Please check the documentation on [the usage of the shared variables](advanced-add-custom-module.md#shared_variables_class), a very important step is described there concerning setting and getting shared variables.

* __[Data Recorder](modules-datarecorder.md)__ - The data recorder is a module that can record data.
* __[CARLA Interface](modules-carlainterface.md)__ - CarlaInterface manages the different agents you can add in simulation.
* __[Hardware Manager](modules-hardwaremanager.md)__ - The hardware manager is a module that manages hardware inputs.
* __[Experiment Manager](modules-experimentmanager.md)__ - The experiment manager is a useful tool for performing experiments
* __[Haptic Controller Manager](modules-hapticcontrollermanager.md)__ - The haptic controller manager is a module that manages haptic (steering wheel) controllers.
* __[Data Plotter](modules-dataplotter.md)__ - The data plotter is a module that easily makes data insightful at runtime.

### Advanced steps
If you want to know more and add to JOAN yourself you can have a look at these sections:

* __[How to create a custom JOAN module](advanced-add-custom-module.md)__ - Guide on how to create your own JOAN modules
* __[JOAN module settings](advanced-settings.md)__ - JOAN uses Settings to save you to set up every module
* __[JOAN state machine](advanced-state-machine.md)__ - Info on JOAN's state machine


### Other documentation
* __[Quick start source control (git)](other-git.md)__ - Quick start guide for source control with git.
* __[SensoDrive explanation](other-sensodrive.md)__ - Some remarks, explanations, and 'best practices' for working with a SENSOWheel SD-LC

### Want to contribute?
* __[Guidelines](contributing-guidelines.md)__ - Guidelines if you want to add to JOAN
* __[Coding Standard](contributing-coding-standard.md)__ - Coding standard for JOAN (we try)
