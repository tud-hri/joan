# JOAN documentation

Welcome to the JOAN human-automated vehicle interaction simulator documentation! This documentation should get you up and running with JOAN and [CARLA](http://carla.org).

JOAN is a software framework that builds upon CARLA, a simulator made to study automated driving, by making CARLA also useful for human-in-the-loop experiments of human drivers and other road users interacting with automated vehicles. 

Among others, we build JOAN to enable you to 

- Quickly set up (human-in-the-loop) experiments, 
- Define traffic scenarios, 
- Log data, and 
- Implement haptic driver-automated vehicle interaction.

Have fun!

!!! Note
    For students at TU Delft, please start reading __[Setup JOAN on a TUD computer](setup-on-tud-shared-hardware.md)__

JOAN is developed by members of the [Human-Robot Interaction group](https://delfthapticslab.nl) at Cognitive Robotics of Delft University of Technology.

Below a video of some of the capabilities of JOAN is shown, one of the main software components of the Symbiotic Driving Demonstrator was JOAN :)!ssssssss

---

<iframe width="560" height="315" src="https://www.youtube.com/embed/xcGXE7rI61s" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

--- 

## Useful links

- Because JOAN depends heavily on CARLA, we strongly recommend you to check out the [CARLA documentation](https://carla.readthedocs.io/en/latest/). 
- You can find the JOAN repository [here][repolink]. Note that JOAN is still under development, so core functionality may change over time. We'll post releases as soon as we think we are ready :-)

[repolink]: https://gitlab.tudelft.nl/tud-cor-hri/joan-framework/joan

--- 

## Setup JOAN and CARLA
Thorough guide on setting up JOAN and CARLA:

* __[Setting up CARLA on Windows](setup-carla-windows.md)__ - The most important steps from the CARLA documentation
* __[Setting up JOAN](setup-joan.md)__ -- Install JOAN
* __[Setup JOAN on a TUD computer](setup-on-tud-shared-hardware.md)__ - guide on how to install your project on TUD shared hardware (probably your first step)

## First steps
If you want to build up an understanding of JOAN the sections below are a good place to start:

* __[JOAN Overview](firststeps-joan-overview.md)__ - Core, Modules, Dataflow
* __[Quick Start Running Joan and CARLA](firststeps-joan-run.md)__ - Quickstart on how to run JOAN and CARLA
* __[Quick start CARLA environment](firststeps-carle-ue4.md)__ - Quickstart on CARLA and the Unreal Editor

## Using the JOAN modules
Several modules are included with JOAN by default, the way to use them is described in their seperate sections:

* __[Data Recorder](modules-datarecorder.md)__ - The data recorder is a module which can record data.
* __[CARLA Interface](modules-carlainterface.md)__ - The experiment manager is a useful tool for performing experiments
* __[Experiment Manager](modules-hardwaremanager.md)__ - The hardware manager is a module which manages hardware inptus
* __[Haptic Controller Manager](modules-hapticcontrollermanager.md)__ - The haptic controller manager is a module which manages haptic (steering wheel) controllers.
* __[Data Plotter](modules-dataplotter.md)__ - The data plotter is a module which easily makes data insightful at runtime.

## Advanced steps
If you want to know more and add to JOAN yourself you can have a look at these sections:

* __[How to create a custom JOAN module](advancedsteps-add-custom-module.md)__ - Guide on how to create your own JOAN modules
* __[JOAN module settings](advancedsteps-settings.md)__ - JOAN uses Settings to save you to set up every module
* __[JOAN state machine](advancedsteps-state-machine.md)__ - Info on JOAN's state machine


## Other documentation
* __[Quick start source control (git)](other-git.md)__ - Quick start guide for source control with git.
* __[SensoDrive explanation](other-sensodrive.md)__ - Some remarks/explanation and 'best practices' for working with a SENSO Wheel SD-LC

## Want to contribute?
* __[Guidelines](contributing-guidelines.md)__ - Guidelines if you want to add to JOAN
* __[Coding Standard](contributing-coding-standard.md)__ - Coding standard for JOAN (we try)
